import asyncio
from bot.utils.music_utils import (
    extract_audio,
    get_or_create_queue,
    playback_tasks,
    start_playback,
)
from discord import app_commands, Interaction, Object

queues = {}
playback_tasks = {}


@app_commands.command(
    name="play",
    description="Plays a YouTube URL's audio, adds to a queue if one is playing already.",
)
@app_commands.describe(url="YouTube video URL to play.")
async def play(interaction: Interaction, url: str):
    await interaction.response.defer()

    try:
        audio_url, title = extract_audio(url)
    except Exception as e:
        await interaction.followup.send("Could not get audio.")
        print(e)
        return

    guild_id = interaction.guild_id
    voice_client = interaction.guild.voice_client
    queue = await get_or_create_queue(interaction.guild.id)
    await queue.put((audio_url, title))

    if (
        not voice_client
        or not voice_client.is_connected()
        or not voice_client.is_playing()
    ):
        if (
            guild_id not in playback_tasks
            or playback_tasks[interaction.guild.id].done()
        ):
            playback_tasks[interaction.guild.id] = asyncio.create_task(
                start_playback(interaction)
            )
    else:
        await interaction.followup.send(f"Queued: **{title}**")


async def setup(tree: app_commands.CommandTree, guild_id: int):
    tree.add_command(play, guild=Object(id=guild_id))
