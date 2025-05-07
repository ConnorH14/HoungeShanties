import yt_dlp
import discord
import asyncio

queues = {}
playback_tasks = {}


async def get_or_create_queue(guild_id: int):
    if guild_id not in queues:
        queues[guild_id] = asyncio.Queue()
    return queues[guild_id]


def extract_audio(url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "default_search": "auto",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"], info.get("title", "Unknown")


async def connect_to_voice(interaction: discord.Interaction):
    guild = interaction.guild
    voice_state = interaction.user.voice

    if voice_state and voice_state.channel:
        channel = voice_state.channel
    else:
        active = [vc for vc in guild.voice_channels if len(vc.members) > 0]
        if not active:
            return None, "No active voice channels."
        channel = active[0]

    voice_client = guild.voice_client
    if not voice_client or not voice_client.is_connected():
        voice_client = await channel.connect()
    elif voice_client.channel != channel:
        await voice_client.move_to(channel)

    return voice_client, None


async def start_playback(interaction: discord.Interaction):
    guild = interaction.guild
    queue = await get_or_create_queue(guild.id)

    voice_client, err = await connect_to_voice(interaction)
    if err:
        await interaction.followup.send("Could not start playback.")
        print(err)
        return

    while not queue.empty():
        url, title = await queue.get()
        done = asyncio.Event()

        source = discord.FFmpegPCMAudio(
            url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        )

        def after(_):
            done.set()

        voice_client.play(source, after=lambda e: after(e))
        await interaction.followup.send(f"Now playing: **{title}**")
        await done.wait()
