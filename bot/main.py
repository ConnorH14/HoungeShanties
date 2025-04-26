import discord
from discord.ext import commands
import asyncio
from bot.config import TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
  initial_extensions = [
    'bot.commands.ping',
    'bot.events.on_ready',
  ]

  for extension in initial_extensions:
    await bot.load_extension(extension)

@bot.event
async def on_ready():
  await print(f"Logged in as {bot.user}!")

async def main():
  async with bot:
    await load_extensions()
    await bot.start(TOKEN)

if __name__ == "__main__":
  asyncio.run(main())