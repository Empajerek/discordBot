import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

activeUsers = 0  

async def initUsersState(guild):
    global activeUsers
    activeUsers = 0 
    for member in guild.members:
        if member.voice is not None:
            activeUsers  += 1
    print(activeUsers)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    await initUsersState(guild)

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot == True:
        return

    if "mouthbreather" in message.content.split(" "):
        response = f"pls don't offend me."
        await message.channel.send(response)
    else:
        response = f"<@{message.author.id}> said {message.content}"
        await message.channel.send(response)

@client.event
async def on_voice_state_update(member, before, after):
    global activeUsers
    if before.channel is None and after.channel is not None:
        activeUsers += 1
    if before.channel is not None and after.channel is None:
        activeUsers -= 1
    for channel in member.guild.channels:
        if channel.name == 'tuba-nagłaśniająca':
            try:
                message = await message.edit(content=f"There are now {activeUsers} in vc, come on join them!")
            except UnboundLocalError:
                message =  await channel.send(f"There are now {activeUsers} in vc, come on join them!")

client.run(TOKEN)