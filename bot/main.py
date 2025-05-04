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


@client.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
):
    voice_client = member.guild.voice_client
    if not voice_client or not voice_client.is_connected():
        return

    bot_channel = voice_client.channel

    if (
        len(bot_channel.members) == 1
        and bot_channel.members[0] == member.guild.me
    ):
        await voice_client.disconnect()
        print(f"Disconnected from {bot_channel.name} because it was empty.")


client.run(TOKEN)
