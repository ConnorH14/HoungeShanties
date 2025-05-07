import os
import asyncio
from discord import app_commands, Interaction, Object
from bot.config import PLAYLIST_DIR
from bot.utils.music_utils import (
    get_or_create_queue,
    extract_audio,
    playback_tasks,
    start_playback,
)

os.makedirs(PLAYLIST_DIR, exist_ok=True)


class PlaylistGroup(app_commands.Group):
    def __init__(self):
        super().__init__(
            name="playlist", description="Manage your personal music playlist."
        )

    @app_commands.command(
        name="add",
        description="Add a video URL to your personal playlist.",
    )
    @app_commands.describe(url="Youtube URL to add")
    async def add(self, interaction: Interaction, url: str):
        await interaction.response.defer()

        if not url.startswith("http"):
            await interaction.followup.send("Please provide a valid URL.")
            return

        user_file = os.path.join(PLAYLIST_DIR, f"{interaction.user.id}.txt")

        with open(user_file, "a", encoding="utf-8") as f:
            f.write(url.strip() + "\n")

        await interaction.followup.send("Added to your personal playlist.")

    @app_commands.command(name="view", description="View your playlist URLs.")
    async def view(self, interaction: Interaction):
        user_file = os.path.join(PLAYLIST_DIR, f"{interaction.user.id}.txt")
        if not os.path.exists(user_file) or os.path.getsize(user_file) == 0:
            await interaction.response.send_message("Your playlist is empty.")
            return

        with open(user_file, "r", encoding="utf-8") as f:
            entries = [
                f"{i+1}. <{line.strip()}>"
                for i, line in enumerate(f.readlines())
            ]

            msg = "\n".join(entries[:20])
            await interaction.response.send_message(f"Your Playlist: \n{msg}")

    @app_commands.command(
        name="play",
        description="Play all the songs in your personal playlist.",
    )
    async def play(self, interaction: Interaction):
        await interaction.response.defer()

        user_file = os.path.join(PLAYLIST_DIR, f"{interaction.user.id}.txt")
        if not os.path.exists(user_file):
            await interaction.followup.send(
                "No playlist found. Use `/playlist add` to add songs."
            )
            return

        with open(user_file, "r", encoding="utf-8") as f:
            links = [line.strip() for line in f if line.strip()]

        if not links:
            await interaction.followup.send("Your playlist is empty.")
            return

        guild_id = interaction.guild.id
        queue = await get_or_create_queue(guild_id)
        voice_client = interaction.guild.voice_client
        first_song = not voice_client or not voice_client.is_playing()

        added = 0
        for url in links:
            try:
                audio_url, title = extract_audio(url)
                await queue.put((audio_url, title))
                added += 1
            except Exception as e:
                await interaction.followup.send(f"Failed to play link.")
                print(e)
                return

        await interaction.followup.send(
            f"Added {added} song(s) from your playlist."
        )

        if first_song:
            playback_tasks[guild_id] = asyncio.create_task(
                start_playback(interaction)
            )

    @app_commands.command(
        name="clear", description="Clear all URLs from your playlist."
    )
    async def clear(self, interaction: Interaction):
        user_file = os.path.join(PLAYLIST_DIR, f"{interaction.user.id}.txt")
        if not os.path.exists(user_file) or os.path.getsize(user_file) == 0:
            await interaction.response.send_message(
                "Your playlist is already empty."
            )
            return

        await interaction.response.send_message(
            "Are you sure you want to clear your entire playlist? React with ✅ to confirm or ❌ to cancel."
        )

        confirmation_message = await interaction.original_response()

        await confirmation_message.add_reaction("✅")
        await confirmation_message.add_reaction("❌")

        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in [
                "✅",
                "❌",
            ]

        try:
            reaction, _ = await interaction.client.wait_for(
                "reaction_add", check=check, timeout=60
            )

            if str(reaction.emoji) == "✅":
                with open(user_file, "w", encoding="utf-8") as f:
                    f.truncate(0)
                await interaction.followup.send(
                    "Your playlist has been cleared."
                )
            else:
                await interaction.followup.send(
                    "Action canceled. Your playlist was not cleared."
                )
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "You took too long to respond. Your playlist was not cleared."
            )

    @app_commands.command(
        name="remove", description="Remove a specific song from your playlist."
    )
    @app_commands.describe(
        song_number="The number of the song you want to remove (e.g., 1, 2, 3...)"
    )
    async def remove(self, interaction: Interaction, song_number: int):
        user_file = os.path.join(PLAYLIST_DIR, f"{interaction.user.id}.txt")
        if not os.path.exists(user_file) or os.path.getsize(user_file) == 0:
            await interaction.response.send_message("Your playlist is empty")
            return

        with open(user_file, "r", encoding="utf-8") as f:
            playlist = f.readlines()

        if song_number < 1 or song_number > len(playlist):
            await interaction.response.send_message(
                f"Invalid song number. Your playlist has {len(playlist)} song(s)."
            )
            return

        song_to_remove = playlist.pop(song_number - 1)

        with open(user_file, "w", encoding="utf-8") as f:
            f.writelines(playlist)

        await interaction.response.send_message(
            f"Removed song: {song_to_remove.strip()} from your playlist."
        )


playlist_group = PlaylistGroup()


async def setup(tree: app_commands.CommandTree, guild_id: int):
    tree.add_command(playlist_group, guild=Object(id=guild_id))
