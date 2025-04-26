from discord.ext import commands

class ReadyEvent(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_ready(self):
    await print(f"{self.bot.user} is connected and ready!")

async def setup(bot):
  await bot.add_cog(ReadyEvent(bot))