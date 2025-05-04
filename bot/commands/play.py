import discord
import yt_dlp
from discord import app_commands


@discord.app_commands.command(
    name="play", description="Plays a song from a given URL."
)
@app_commands.describe(url="Add a YouTube URL.")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    guild = interaction.guild
    if not guild:
        await interaction.followup.send(
            "This command must be used in a server."
        )
        return

    voice_state = interaction.user.voice
    if voice_state and voice_state.channel:
        target_vc = voice_state.channel
    else:
        active_vcs = [vc for vc in guild.voice_channels if len(vc.members) > 0]
        if not active_vcs:
            await interaction.followup.send("No one is in a voice channel.")
            return
        target_vc = active_vcs[0]

    voice_client = guild.voice_client
    if not voice_client or not voice_client.is_connected():
        try:
            voice_client = await target_vc.connect()
        except Exception as e:
            await interaction.followup.send(f"Failed to join voice channel.")
            print(e)
            return

    elif voice_client.channel != target_vc:
        await voice_client.move_to(target_vc)

    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "extract_flat": "in_playlist",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]
            title = info.get("title", "Unknown")

        source = discord.FFmpegPCMAudio(
            audio_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        )
        voice_client.stop()
        voice_client.play(source)

        await interaction.followup.send(f"Now playing: **{title}**")

    except Exception as e:
        await interaction.followup.send(f"Failed to play audio.")
        print(e)


async def setup(tree: discord.app_commands.CommandTree, guild_id: int):
    tree.add_command(play, guild=discord.Object(id=guild_id))
