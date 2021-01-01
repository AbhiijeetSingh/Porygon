
import discord
from discord import file
from discord.ext import commands
from discord.ext.commands.core import command
import audioDL
import os
import key
import asyncio
from youtube_dl import YoutubeDL

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


# @client.event
# async def on_command_error(ctx, error):
#     # sends the error encountered on the discord
#     # channel called from
#     await ctx.send(f"{error}")


# @client.command()
# async def songsDL(ctx, link):
#     # Downloads the songs from youtube using
#     # youtube-dl and converts them to mp3 and later
#     # uploads them back to the discord channel
#     # upon upload deletes the file from the
#     # pc/server (works with links only)
#     await ctx.send("Downloading song(s) (might take sometime to download, be patient.)")
#     if audioDL.song_download(link) == 0:
#         await ctx.send(f"{ctx.author.mention}Song(s) Downloaded----Uploading now. (just a few more seconds \N{WINKING FACE} )")
#         path = "DL_songs/"
#         filenames = os.listdir(path)
#         for filename in filenames:
#             await ctx.send(file=discord.File(path+filename))
#             print(f"{filename} uploaded")
#             os.remove(path+filename)
#             print(f"{filename} deleted successfully")


# @client.command()
# async def clear(ctx, amount: int = 2):
#     # is used to clear the texts/messages sent
#     # in the discord channel.
#     await ctx.channel.purge(limit=amount)
#     await ctx.send(f"{amount} message(s) cleared")
#     print(f"{amount} message(s) cleared")


# @client.command()
# async def playDL(ctx, *, usersearch):
#     # Downloads songs from youtube using
#     # youtube-dl and ytsearch function
#     # and uploads them back to the discord
#     # channel (takes the name/reference of the song)
#     await ctx.send("Downloading song")
#     if audioDL.search_download(usersearch) == 0:
#         await ctx.send(f"{ctx.author.mention} Song Downloaded----Playing now\N{SLIGHTLY SMILING FACE}.")
#         path = "DL_songs/"
#         filename = os.listdir(path)[0]
#         channel = ctx.author.voice.channel
#         source = discord.FFmpegPCMAudio(path+filename)
#         if channel is None:
#             await ctx.send("Please join a voice channel")
#         else:
#             vc = await channel.connect()
#             vc.play(source)
#             while not vc.is_playing():
#                 print(f"{filename} deleted")
#                 os.remove(filename)


# @client.command()
# async def clearLIB(ctx):
#     path = "DL_songs/"
#     filenames = os.listdir(path)
#     file_index = 0
#     for filename in filenames:
#         os.remove(path+filename)
#         file_index += 1
#     await ctx.send(f"{file_index} file(s) removed")


# @client.command()
# async def play(ctx, *, usersearch):
#     channel = ctx.author.voice.channel
#     if channel is None:
#         await ctx.send("Please join a voice channel")
#     else:
#         await channel.connect()
#     FFMPEG_OPTS = {
#         'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
#     title, audio_url = audioDL.search_stream(usersearch)
#     source = discord.FFmpegPCMAudio(source=audio_url, **FFMPEG_OPTS)
#     await ctx.send(f'Now playing {title}.')
#     ctx.voice_client.play(source)


class MusicStreamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = dict()

    @commands.command()
    async def play(self, ctx, *query):
        query = " ".join(query)
        channel = ctx.author.voice.channel
        
        if channel is None:
            async with ctx.typing():
                await ctx.send("Please join a voice channel first.")
        
        else:
            voice_client = await channel.connect()
            
            with YoutubeDL({"format": "bestaudio", "noplaylist": "True"}) as yt_dl:
                extract_info_lambda = lambda:yt_dl.extract_info({f"ytsearch:{query}"}, download=False)
                event_loop = asyncio.get_event_loop()
                youtube_info = await event_loop.run_in_executor(None, extract_info_lambda)
                
            async with ctx.typing():
                await ctx.send(f"Now playing {youtube_info['title']}")
            
            FFMPEG_OPTS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
                }

            source = discord.FFmpegPCMAudio(source=youtube_info['formats'][0]['url'], **FFMPEG_OPTS)
            self.voice_clients[ctx.guild.id] = voice_client
            voice_client.play(source)

    @commands.command()
    async def pause(self, ctx):
        if ctx.guild.id in self.voice_clients:
            self.voice_clients.get(ctx.guild.id).pause()
        else:
            async with ctx.typing():
                await ctx.send("You need to play something first.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.guild.id in self.voice_clients:
            self.voice_clients.get(ctx.guild.id).resume()
        else:
            async with ctx.typing():
                await ctx.send("You need to play something first.")

client.add_cog(MusicStreamingCog(client))
client.run(key.bot_key)
