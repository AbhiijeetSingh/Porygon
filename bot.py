import discord
from player import Player
from discord.ext import commands
from audio_repo import AudioRepo
import key
import asyncio
from song import Song
from aiohttp import ClientSessiion

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


class NekoLifeCog(object):
    def __init__(self, bot):
        self.bot = bot
        self.BASE_URL = "https://nekos.life/api/v2/"
        self.SFW = {
            "tickle": "/img/tickle",
            "slap": "/img/slap",
            "poke": "/img/poke",
            "pat": "/img/pat",
            "neko": "/img/neko",
            "meow": "/img/meow",
            "lizard": "/img/lizard",
            "kiss": "/img/kiss",
            "hug": "/img/hug",
            "foxGirl": "/img/fox_girl",
            "feed": "/img/feed",
            "cuddle": "/img/cuddle",
            "why": "/why",
            "catText": "/cat",
            "OwOify": "/owoify",
            "8Ball": "/8ball",
            "fact": "/fact",
            "nekoGif": "/img/ngif",
            "kemonomimi": "/img/kemonomimi",
            "holo": "/img/holo",
            "smug": "/img/smug",
            "baka": "/img/baka",
            "woof": "/img/woof",
            "spoiler": "/spoiler",
            "wallpaper": "/img/wallpaper",
            "goose": "/img/goose",
            "gecg": "/img/gecg",
            "avatar": "/img/avatar",
            "waifu": "/img/waifu"
        }
        self.NSFW = {
            "randomHentaiGif": "/img/Random_hentai_gif",
            "pussy": "/img/pussy",
            "nekoGif": "/img/nsfw_neko_gif",
            "neko": "/img/lewd",
            "lesbian": "/img/les",
            "kuni": "/img/kuni",
            "cumsluts": "/img/cum",
            "classic": "/img/classic",
            "boobs": "/img/boobs",
            "bJ": "/img/bj",
            "anal": "/img/anal",
            "avatar": "/img/nsfw_avatar",
            "yuri": "/img/yuri",
            "trap": "/img/trap",
            "tits": "/img/tits",
            "girlSoloGif": "/img/solog",
            "girlSolo": "/img/solo",
            "pussyWankGif": "/img/pwankg",
            "pussyArt": "/img/pussy_jpg",
            "kemonomimi": "/img/lewdkemo",
            "kitsune": "/img/lewdk",
            "keta": "/img/keta",
            "holo": "/img/hololewd",
            "holoEro": "/img/holoero",
            "hentai": "/img/hentai",
            "futanari": "/img/futanari",
            "femdom": "/img/femdom",
            "feetGif": "/img/feetg",
            "eroFeet": "/img/erofeet",
            "feet": "/img/feet",
            "ero": "/img/ero",
            "eroKitsune": "/img/erok",
            "eroKemonomimi": "/img/erokemo",
            "eroNeko": "/img/eron",
            "eroYuri": "/img/eroyuri",
            "cumArts": "/img/cum_jpg",
            "blowJob": "/img/blowjob",
            "spank": "/img/spank",
            "gasm": "/img/gasm"
        }

    async def get(self, endpoint):
        async with ClientSessiion() as session:
            resp = await session.get(f"{self.BASE_URL}{endpoint_url}")
            json = await resp.json()
            if 'url' not in json.keys():
                raise Exception
            image_resp = await session.get(json['url'])

    @commands.command()
    async def neko(self, ctx, tag=None):
        endpoint_url = self.SFW.get(tag, None) or "img/neko" 
        async with ClientSessiion() as session:
            resp = await session.get(f"{self.BASE_URL}{endpoint_url}")
            json = await resp.json()

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

    @commands.command()
    async def play(self, ctx, *query):
        query = " ".join(query)
        voice_client = ctx.voice_client

        info = await self.audio_repo.get_info(query)
        source = await self.audio_repo.get(info)

        title = info['entries'][0]['title']
        song = Song(
            title=title,
            source=source,
            context=ctx,
        )

        embed = discord.Embed(
            title="Added to queue",
            description=title,
            color=0x00DAFF                
        ).set_thumbnail(url=info['entries'][0]['thumbnail'])

        if self.players[ctx.guild.id].get_queue_length() != 0:
            await ctx.send(embed=embed)

        await self.players[ctx.guild.id].add_to_queue(song)

            # async with ctx.typing():
            #     await ctx.send(embed=embed)

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

    @commands.command()
    async def pause(self, ctx):
        await self.players[ctx.guild.id].pause(ctx)

    @commands.command()
    async def resume(self, ctx):
        await self.players[ctx.guild.id].resume(ctx)

    @commands.command()
    async def disconnect(self, ctx):
        await self.players[ctx.guild.id].disconnect(ctx)

    @commands.command()
    async def next(self, ctx):
        self.players[ctx.guild.id].next(ctx)
    
    @commands.command()
    async def loop(self, ctx):
        self.players[ctx.guild.id].loop(ctx)


if __name__ == "__main__":
    client.add_cog(MusicStreamingCog(client))
    client.run(key.bot_key)