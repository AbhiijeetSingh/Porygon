
import discord
from discord.ext import commands
import audioDL
import os
import key
import youtube_dl
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

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
        channel=ctx.author.voice.channel
        for filename in filenames:
            source=discord.FFmpegPCMAudio(path+filename)
            await channel.connect()
            ctx.voice_client.play(source)
            # await ctx.send(file=discord.File(path+filename))
            # print(f"{filename} uploaded")
            # os.remove(path+filename)
            # print(f"{filename} deleted successfully")


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class StreamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print(
            'Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def yt(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player, after=lambda e: print(
                'Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(
                'Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


client.add_cog(StreamingCog(client))
client.run(key.bot_key)
