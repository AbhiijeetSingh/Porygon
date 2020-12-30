
import discord
from discord.ext import commands
import time
import audioDL
import os
import random
import asyncio
import key

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=">")


@client.event
async def on_ready():
    # passes the "ready" comment in the terminal
    # on starting
    print("Porygon is ready")


@client.event
async def on_member_join(member):
    # passes name of the member that joined the server
    print(f"{member} has joined the server")


@client.event
async def on_member_remove(member):
    # passes the name of the member that left the server
    print(f"{member} has left the server")


@client.event
async def on_command_error(ctx, error):
    # sends the error encountered on the discord
    # channel called from
    await ctx.send(f"{error}")


@client.command()
async def songsDL(ctx, link):
    # Downloads the songs from youtube using
    # youtube-dl and converts them to mp3 and later
    # uploads them back to the discord channel
    # upon upload deletes the file from the
    # pc/server (works with links only)
    await ctx.send("Downloading song(s) (might take sometime to download, be patient.)")
    if audioDL.song_download(link) == 0:
        await ctx.send(f"{ctx.author.mention}Song(s) Downloaded----Uploading now. (just a few more seconds \N{WINKING FACE} )")
        path = "DL_songs/"
        filenames = os.listdir(path)
        for filename in filenames:
            await ctx.send(file=discord.File(path+filename))
            print(f"{filename} uploaded")
            os.remove(path+filename)
            print(f"{filename} deleted successfully")


@client.command()
async def clear(ctx, amount: int = 2):
    # is used to clear the texts/messages sent
    # in the discord channel.
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"{amount} message(s) cleared")
    print(f"{amount} message(s) cleared")


@client.command()
async def searchDL(ctx, *, usersearch):
    # Downloads songs from youtube using
    # youtube-dl and ytsearch function
    # and uploads them back to the discord
    # channel (takes the name/reference of the song)
    await ctx.send("Downloading song")
    if audioDL.search_download(usersearch) == 0:
        await ctx.send(f"{ctx.author.mention} Song Downloaded----Uploading now\N{SLIGHTLY SMILING FACE}.")
        path = "DL_songs/"
        filenames = os.listdir(path)
        for filename in filenames:
            await ctx.send(file=discord.File(path+filename))
            print(f"{filename} uploaded")
            os.remove(path+filename)
            print(f"{filename} deleted successfully")


client.run(key.bot_key)
