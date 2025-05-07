from discord import app_commands, Interaction, Object
from bot.utils.music_utils import queues


@app_commands.command(
    name="stop", description="Stops the music and clears the queue."
)
async def stop(interaction: Interaction):
    await interaction.response.defer()

    guild = interaction.guild
    voice_client = guild.voice_client

    if not voice_client or not voice_client.is_connected():
        await interaction.followup.send("I'm not in a voice channel.")
        return

    if voice_client.is_playing():
        voice_client.stop()

    queue = queues.get(guild.id)
    if queue:
        while not queue.empty():
            queue._queue.clear()

    await interaction.followup.send("Stopped playback and cleared the queue.")


async def setup(tree: app_commands.CommandTree, guild_id: int):
    tree.add_command(stop, guild=Object(id=guild_id))
