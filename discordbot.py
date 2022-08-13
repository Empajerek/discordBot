#!/usr/bin/env python3

from email import message
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

notification_role = "779352944919183393"
notification_channel = "1007685204162396181"
global StatMessage
songQueue = []
alreadyPlaying = False

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='KWA ',intents=intents)

async def musicBot(ctx, songName, channel):
    voice = discord.utils.get(ctx.guild.voice_channels, name=channel.name)

    voice_client = ctx.voice_client

    if voice_client == None:
        voice_client = await voice.connect()
    else:
        await voice_client.move_to(channel)

    songName = songName.replace(" ", "+")

    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + songName)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

        
    message = await ctx.send("https://www.youtube.com/watch?v=" + video_ids[0])

    song = pafy.new(video_ids[0])

    audio = song.getbestaudio()

    source = FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)

    voice_client.play(source)

    return message

async def initUsersState(guild):
    global activeUsers
    activeUsers = 0 
    for member in guild.members:
        if member.voice is not None:
            activeUsers  += 1

#init
@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user} dołączył do:\n{guild.name}(id: {guild.id})')
    await initUsersState(guild)

#simple pause
@bot.command(brief="Zatrzymuje graną piosenkę.")
async def pauza(ctx):
    try:
        await ctx.send(f"Taka przerwa też w sumie jest spoko!")
        ctx.voice_client.pause()
    except:
        await ctx.send(f"{ctx.author.mention} nic przecież nie gram!")

#show song queue
@bot.command(brief="Wyświetla listę następnych kawałków.")
async def następny(ctx):
    global songQueue
    st = ""
    for i in songQueue:
        st += f"\n- {i}"
    await ctx.send(f"Na liście jest jeszcze {len(songQueue)} kawałków.\n A wśród nich: {st}")

#simple pause
@bot.command(brief="Wznawia graną piosenkę.")
async def wznów(ctx):
    try:
        await ctx.send(f"Lecimy maestro!")
        ctx.voice_client.resume()
    except:
        await ctx.send(f"{ctx.author.mention} nic przecież nie gram!")

#song skip
@bot.command(brief="Wznawia graną piosenkę.")
async def pomiń(ctx):
    try:
        await ctx.send(f"Pomijamy!")
        ctx.voice_client.stop()
    except:
        await ctx.send(f"{ctx.author.mention} nic przecież nie gram!")

#music bot
@bot.command(brief="Gra piosenkę na podstawie podanego hasła.")
async def zagraj(ctx, *, arg):
    global alreadyPlaying, songQueue
    if alreadyPlaying:
        await ctx.send(f"Dopisuje już do listy, wariacie!\n\"{str(arg)}\"\n<@{ctx.author.id}>")
        songQueue.append(arg)
        return

    if ctx.author.voice is None:
        await ctx.send(f"Nie wiem gdzie.\nMusisz gdzieś być abym ci zagrał ziomeczku!\n<@{ctx.author.id}>")
        return
    channel = ctx.author.voice.channel

    alreadyPlaying = True
    message = await musicBot(ctx, arg, channel)

    while ctx.voice_client.is_connected():
        if len(ctx.voice_client.channel.members) == 1:
            await ctx.voice_client.disconnect()
            try:
                await message.delete()
            except:
                pass
            break
        elif ctx.voice_client.is_paused():
            await asyncio.sleep(1)
        elif ctx.voice_client.is_playing():
            await asyncio.sleep(1)
        else:
            try:
                await message.delete()
            except:
                pass
            if len(songQueue):
                song = songQueue.pop()
                await musicBot(ctx,song,channel)
                await asyncio.sleep(1)
            else:
                alreadyPlaying = False
                await ctx.voice_client.disconnect()
                break

#simple responder
@bot.command(brief="Odpowiadam.")
@commands.has_role('Botyk')
async def odpowiedz(ctx, *, arg):
    if ctx.author == bot.user or ctx.author.bot == True:
        return

    if "mouthbreather" in arg.split(" "):
        response = f"pls don't offend me."
        await ctx.send(response)
    else:
        response = f'<@{ctx.author.id}> powiedział {"".join(arg)}'
        await ctx.channel.send(response)

#update
@bot.command(brief="Aktualizuje.")
@commands.has_role('Botyk')
async def aktualizuj(ctx):
    await ctx.send(f"Już się robi szefie!")
    os.execl("./bot.sh","bot.sh")


#notification bot
@bot.event
async def on_voice_state_update(member, before, after):
    global activeUsers, notification_role,StatMessage, notification_channel
    if before.channel is None and after.channel is not None:
        activeUsers += 1
    if before.channel is not None and after.channel is None:
        activeUsers -= 1
    for channel in member.guild.channels:
        if str(channel.id) == notification_channel:
            if activeUsers:
                try:
                    if activeUsers > 1:
                        await StatMessage.edit(content=f"🎙️Właśnie są {activeUsers} osoby na czacie, wbijaj!\n<@&{notification_role}>")
                    else:
                        await StatMessage.edit(content=f"🎙️Właśnie jest jedna osoba na czacie, wbijaj!\n<@&{notification_role}>")
                except (NameError, discord.errors.NotFound):
                    if activeUsers > 1:
                        StatMessage =  await channel.send(f"🎙️Właśnie są {activeUsers} osoby na czacie, wbijaj!\n<@&{notification_role}>")
                    else:
                        StatMessage =  await channel.send(f"🎙️Właśnie jest jedna osoba na czacie, wbijaj!\n<@&{notification_role}>")
            else:
                try:
                    await StatMessage.delete()
                except (NameError, discord.errors.NotFound):
                    pass

bot.run(TOKEN)