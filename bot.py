import discord
from player import Player
from discord.ext import commands
from audio_repo import AudioRepo, clear_repo
import key
import asyncio
from song import Song
from aiohttp import ClientSession
import endpoints

client = commands.Bot(command_prefix=">")


@client.event
async def on_ready():
    # passes the "ready" comment in the terminal
    # on starting
    print("Porygon is ready")
    activity_type = discord.ActivityType.watching
    activity = discord.Activity(
        name="Hmmmmm",
        type=activity_type)
    await client.change_presence(activity=activity)


@client.event
async def on_member_join(member):
    # passes name of the member that joined the server
    print(f"{member} has joined the server")


@client.event
async def on_member_remove(member):
    # passes the name of the member that left the server
    print(f"{member} has left the server")


class MiscCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="clearById", aliases=['cbid'])
    async def clear_by_id(self, ctx, id):
        # Deletes specific text/message
        # based on the message ID.
        channel = ctx.channel
        message = await channel.fetch_message(id)
        await message.delete()
        embed = discord.Embed(
            description=f"Deleted message with ID ...{id[-6:]}.",
            color=0xFF0017)
        await ctx.send(embed=embed)

    @commands.command()
    async def clear(self, ctx, limit: int = 2):
        # is used to clear the texts/messages sent
        # by the bot in the discord channel.
        channel = ctx.channel
        deleted = await channel.purge(
            limit=limit,
            check=lambda m: m.author.id == self.bot.user.id)
        embed = discord.Embed(
            description=f"Deleted {len(deleted)} message(s).",
            color=0xFF0017)
        await ctx.send(embed=embed)


class APIAccessBase(object):
    def __init__(self):
        pass

    async def get_url(self, endpoint_url, headers={}):
        async with ClientSession(headers=headers) as session:
            resp = await session.get(self.base_url+endpoint_url)
            json = await resp.json()
            return json["url"]

    async def get(self, url, headers={}):
        async with ClientSession(headers=headers) as session:
            resp = await session.get(url)
            return resp


class WaifuPicsCog(commands.Cog, APIAccessBase):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.SFW = endpoints.waifu_sfw
        self.NSFW = endpoints.waifu_nsfw

    @commands.command()
    async def waifu(self, ctx, tag=None):
        endpoint_url = self.SFW.get(tag, None) or "sfw/waifu"
        image_url = await self.get_url(endpoint_url)
        await ctx.send(embed=discord.Embed().set_image(url=image_url))

    @commands.command()
    async def waifuLewd(self, ctx, tag=None):
        endpoint_url = self.NSFW.get(tag, None) or "nsfw/waifu"
        image_url = await self.get_url(endpoint_url)
        await ctx.send(embed=discord.Embed().set_image(url=image_url))

    @property
    def base_url(self):
        return "https://waifu.pics/api/"


class NekoLifeCog(commands.Cog, APIAccessBase):
    def __init__(self, bot):
        self.bot = bot
        self.SFW = endpoints.neko_sfw
        self.NSFW = endpoints.neko_nsfw

    @commands.command()
    async def neko(self, ctx, tag=None):
        endpoint_url = self.SFW.get(tag, None) or "img/neko"
        image_url = await self.get_url(endpoint_url)
        await ctx.send(embed=discord.Embed().set_image(url=image_url))

    @commands.command()
    async def nekoLewd(self, ctx, tag=None):
        endpoint_url = self.NSFW.get(tag, None) or "img/lewd"
        image_url = await self.get_url(endpoint_url)
        await ctx.send(embed=discord.Embed().set_image(url=image_url))

    @property
    def base_url(self):
        return "https://nekos.life/api/v2/"


class MusicStreamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_repo = AudioRepo()
        self.players = dict()

    @commands.Cog.listener()
    async def on_ready(self):
        async for guild in self.bot.fetch_guilds():
            self.players[guild.id] = Player(asyncio.Queue())
            asyncio.create_task(self.players[guild.id].start())

    @commands.Cog.listener()
    async def on_connect(self):
        await self.audio_repo.init()

    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.audio_repo.clean_up()

    @commands.command()
    async def play(self, ctx, *query):
        query = " ".join(query)

        info = await self.audio_repo.get_info(query)
        source = await self.audio_repo.get(info)

        title = info['title']
        song = Song(
            title=title,
            source=source,
            context=ctx,
        )

        embed = discord.Embed(
            title="Added to queue",
            description=title,
            color=0x00DAFF
        ).set_thumbnail(url=info['thumbnail'])

        if self.players[ctx.guild.id].get_queue_length() != 0:
            await ctx.send(embed=embed)

        await self.players[ctx.guild.id].enqueue(song)

    @play.before_invoke
    async def ensure_connected_voice_client(self, ctx):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if channel:
            if ctx.voice_client is None:
                await channel.connect()
            if channel.id != ctx.voice_client.channel.id:
                await ctx.send("Bot is in another channel.")
                raise commands.CommandError("Bot is in another channel.")
        else:
            ctx.send("Not connnected to a VC, please connect to a VC")
            raise commands.CommandError("Author not connected to VC.")

    @play.after_invoke
    async def repo_clean_up(self, ctx):
        await self.audio_repo.clean_up()
        
    @commands.command(aliases=['ps'])
    async def pause(self, ctx):
        await self.players[ctx.guild.id].pause(ctx)

    @commands.command(aliases=['r'])
    async def resume(self, ctx):
        await self.players[ctx.guild.id].resume(ctx)

    @commands.command(aliases=['dis'])
    async def disconnect(self, ctx):
        await self.players[ctx.guild.id].disconnect(ctx)
        clear_repo()

    @commands.command(aliases=['n'])
    async def next(self, ctx):
        await self.players[ctx.guild.id].next(ctx)

    @commands.command(aliases=['lp'])
    async def loop(self, ctx):
        await self.players[ctx.guild.id].loop_queue(ctx)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        await self.players[ctx.guild.id].queue_list(ctx)

    @commands.command(aliases=['dq'])
    async def dequeue(self, ctx, *query):
        query = " ".join(query)
        info = await self.audio_repo.get_info(query)
        title = info['title']
        await self.players[ctx.guild.id].dequeue(ctx, title)

    @commands.command(aliases=['cq'])
    async def clearq(self, ctx):
        await self.players[ctx.guild.id].clear_queue(ctx)


if __name__ == "__main__":
    client.add_cog(MusicStreamingCog(client))
    client.add_cog(NekoLifeCog(client))
    client.add_cog(WaifuPicsCog(client))
    client.add_cog(MiscCog(client))
    client.run(key.bot_key)
