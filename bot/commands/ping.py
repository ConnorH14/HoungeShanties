import discord

@discord.app_commands.command(
  name="ping",
  description="Responds with Ping 3!"
)

async def ping(interaction: discord.Interaction):
  await interaction.response.send_message("Ping!")

async def setup(tree: discord.app_commands.CommandTree, guild_id: int):
  tree.add_command(ping, guild=discord.Object(id=guild_id))