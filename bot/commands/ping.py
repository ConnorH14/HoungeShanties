from discord.ext import commands

class PingCommands(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="ping")
  async def ping(self, ctx):
    await ctx.send(f"Ping {ctx.author.mention}")

async def setup(bot):
  await bot.add_cog(PingCommands(bot))