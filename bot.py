
import discord
from discord import file
from discord.ext import commands
import audioDL
import os
import key
import asyncio


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
async def playDL(ctx, *, usersearch):
    # Downloads songs from youtube using
    # youtube-dl and ytsearch function
    # and uploads them back to the discord
    # channel (takes the name/reference of the song)
    await ctx.send("Downloading song")
    if audioDL.search_download(usersearch) == 0:
        await ctx.send(f"{ctx.author.mention} Song Downloaded----Playing now\N{SLIGHTLY SMILING FACE}.")
        path = "DL_songs/"
        filename = os.listdir(path)[0]
        channel = ctx.author.voice.channel
        source = discord.FFmpegPCMAudio(path+filename)
        if channel is None:
            await ctx.send("Please join a voice channel")
        else:
            vc = await channel.connect()
            vc.play(source)
            while not vc.is_playing():
                print(f"{filename} deleted")
                os.remove(filename)


@client.command()
async def clearLIB(ctx):
    path = "DL_songs/"
    filenames = os.listdir(path)
    file_index = 0
    for filename in filenames:
        os.remove(path+filename)
        file_index += 1
    await ctx.send(f"{file_index} file(s) removed")


@client.command()
async def play(ctx, *, usersearch):
    channel = ctx.author.voice.channel
    if channel is None:
        await ctx.send("Please join a voice channel")
    else:
        await channel.connect()
    FFMPEG_OPTS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    title, audio_url = audioDL.search_stream(usersearch)
    source = discord.FFmpegPCMAudio(source=audio_url, **FFMPEG_OPTS)
    await ctx.send(f'Now playing {title}.')
    ctx.voice_client.play(source)


client.run(key.bot_key)
