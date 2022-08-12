#!/usr/bin/env python3

import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

notification_role = "<@&779352944919183393>"
global StatMessage

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='KWA ',intents=intents)

async def initUsersState(guild):
    global activeUsers
    activeUsers = 0 
    for member in guild.members:
        if member.voice is not None:
            print()
            activeUsers  += 1

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    await initUsersState(guild)

@bot.command(name="respond",help="responds with something.")
@commands.has_role('botyk')
async def respond(ctx):
    if ctx.message.author == bot.user or ctx.message.author.bot == True:
        return

    if "mouthbreather" in ctx.message.content.split(" "):
        response = f"pls don't offend me."
        await ctx.send(response)
    else:
        response = f'<@{ctx.message.author.id}> said {"".join(ctx.message.content.split(" ")[2:])}'
        await ctx.channel.send(response)


#notification bot
@bot.event
async def on_voice_state_update(member, before, after):
    global activeUsers, notification_channel,StatMessage
    if before.channel is None and after.channel is not None:
        activeUsers += 1
    if before.channel is not None and after.channel is None:
        activeUsers -= 1
    for channel in member.guild.channels:
        if channel.name == 'tuba-nagłaśniająca':
            if activeUsers:
                try:
                    await StatMessage.edit(content=f"🎙️There are {activeUsers} people currently chatting!\n{notification_role}")
                except (NameError, discord.errors.NotFound):
                    StatMessage =  await channel.send(f"🎙️There are {activeUsers} people currently chatting!\n{notification_role}")
            else:
                try:
                    await StatMessage.delete()
                except (NameError, discord.errors.NotFound):
                    pass
bot.run(TOKEN)