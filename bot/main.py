import discord
from bot.config import TOKEN, GUILD_ID
from bot.utils.loader import load_commands

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
  await tree.sync(guild=discord.Object(id=GUILD_ID))
  print(f"Logged in as {client.user} (ID: {client.user.id})")
  print(f"Synced commands to guild {GUILD_ID}")
  print("--------------------")

@client.event
async def on_connect():
  await load_commands(tree, GUILD_ID)

client.run(TOKEN)