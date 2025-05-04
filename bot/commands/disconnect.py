import discord


@discord.app_commands.command(
    name="disconnect",
    description="Disconnects the bot from the voice channel.",
)
async def disconnect(interaction: discord.Interaction):
    await interaction.response.defer()

    voice_client = (
        interaction.guild.voice_client if interaction.guild else None
    )

    if not voice_client or not voice_client.is_connected():
        await interaction.followup.send(
            "I'm not connected to a voice channel."
        )
        return

    await voice_client.disconnect()
    await interaction.followup.send("Disconnected from the voice channel.")


async def setup(tree: discord.app_commands.CommandTree, guild_id: int):
    tree.add_command(disconnect, guild=discord.Object(id=guild_id))
