#!/usr/bin/env python3

import os
import re
import discord
from dotenv import load_dotenv
from discord.ext import commands
import urllib
import pafy
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import asyncio

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

#need .env file with token and guild
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

notification_role = "<@&779352944919183393>"
global StatMessage

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='KWA ',intents=intents)

async def music_bot(ctx, songName):
    voice = discord.utils.get(ctx.guild.voice_channels, name=channel.name)

    voice_client = ctx.voice_client

    if voice_client == None:
        voice_client = await voice.connect()
    else:
        await voice_client.move_to(channel)

    songName = songName.replace(" ", "+")

    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + songName)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        
    await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])

    song = pafy.new(video_ids[0])

    audio = song.getbestaudio()

    source = FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)

    voice_client.play(source)

    while ctx.voice_client.is_connected():
        if len(ctx.voice_client.channel.members) == 1:
            await ctx.voice_client.disconnect()
            break
        elif ctx.voice_client.is_paused():
            await asyncio.sleep(1)
        elif ctx.voice_client.is_playing():
            await asyncio.sleep(1)
        else:
            await ctx.voice_client.disconnect()
            break

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
    print(f'{bot.user} dołączył do:\n{guild.name}(id: {guild.id})')
    await initUsersState(guild)

@bot.command(brief="Zatrzymuje graną piosenkę.")
async def pauza(ctx):
    try:
        ctx.voice_client.pause()
    except:
        await ctx.send(f"{ctx.author.mention} nic przecierz nie gram!")


@bot.command(brief="Wznawia graną piosenkę.")
async def wznów(ctx):
    try:
        ctx.voice_client.resume()
    except:
        await ctx.send(f"{ctx.author.mention} nic przecierz nie gram!")

@bot.command(brief="Gra piosenkę z podanego linku.")
async def zagraj(ctx, *, arg):
        if ctx.author.voice is None:
            await ctx.send(f"Nie wiem gdzie.\nMusisz gdzieś być abym ci zagrał ziomeczku!\n<@{ctx.author.id}>")
            return
        channel = ctx.author.voice.channel

        voice = discord.utils.get(ctx.guild.voice_channels, name=channel.name)

        voice_client = ctx.voice_client

        if voice_client == None:
            voice_client = await voice.connect()
        else:
            await voice_client.move_to(channel)

        arg = arg.replace(" ", "+")

        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + str(arg))
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        
        await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])

        song = pafy.new(video_ids[0])

        audio = song.getbestaudio()

        source = FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)

        voice_client.play(source)

        while ctx.voice_client.is_connected():
            if len(ctx.voice_client.channel.members) == 1:
                await ctx.voice_client.disconnect()
                break
            elif ctx.voice_client.is_paused():
                await asyncio.sleep(1)
            elif ctx.voice_client.is_playing():
                await asyncio.sleep(1)
            else:
                await ctx.voice_client.disconnect()
                break

@bot.command(brief="Odpowiadam.")
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
                    if activeUsers > 1:
                        await StatMessage.edit(content=f"🎙️Właśnie jest {activeUsers} osoby na czacie, wbijaj!\n{notification_role}")
                    else:
                        await StatMessage.edit(content=f"🎙️Właśnie jest jedna osoba na czacie, wbijaj!\n{notification_role}")
                except (NameError, discord.errors.NotFound):
                    if activeUsers > 1:
                        StatMessage =  await channel.send(f"🎙️Właśnie jest {activeUsers} osoby na czacie, wbijaj!\n{notification_role}")
                    else:
                        StatMessage =  await channel.send(f"🎙️Właśnie jest jedna osoba na czacie, wbijaj!\n{notification_role}")
            else:
                try:
                    await StatMessage.delete()
                except (NameError, discord.errors.NotFound):
                    pass
bot.run(TOKEN)