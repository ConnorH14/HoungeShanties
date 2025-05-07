import discord
from discord import app_commands, Interaction, Object


@app_commands.command(
    name="skip", description="Skips the song currently playing."
)
async def skip(interaction: Interaction):
    await interaction.response.defer()

    voice_client = interaction.guild.voice_client

    if not voice_client or not voice_client.is_connected():
        await interaction.followup.send(
            "I'm not connected to a voice channel."
        )
        return

    if not voice_client.is_playing():
        await interaction.followup.send("Nothing is playing right now.")
        return

    voice_client.stop()
    await interaction.followup.send("Skipped the current song.")


async def setup(tree: app_commands.CommandTree, guild_id: int):
    tree.add_command(skip, guild=Object(id=guild_id))
