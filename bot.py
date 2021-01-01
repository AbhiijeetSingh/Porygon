from concurrent.futures.thread import ThreadPoolExecutor

import discord
from player import Player
from discord.ext import commands
from audio_repo import AudioRepo
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


class MusicStreamingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = dict()
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
        channel = ctx.author.voice.channel if ctx.author.voice else None

        if channel is None:
            async with ctx.typing():
                await ctx.send("Please join a voice channel first.")

        else:
            voice_client_dict = self.voice_clients.get(ctx.guild.id, None)
            voice_client = voice_client_dict or await channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
            queue_length = self.players[ctx.guild.id].get_queue_length()
            message_prefix = "Now playing" if queue_length < 1 else "Added to queue"

            info = await self.audio_repo.get_info(query)

            embed = discord.Embed(
                title = message_prefix,
                description = info['entries'][0]['title'],
                color=0x00DAFF
                ).set_image(info['entries'][0]['thumbnail'])
            
            async with ctx.typing():
                await ctx.send(embed = embed)
            source = await self.audio_repo.get(info)

            await self.players[ctx.guild.id].add_to_queue((source, voice_client))

    @commands.command()
    async def pause(self, ctx):
        if not await self.players[ctx.guild.id].pause():
            async with ctx.typing():
                await ctx.send("You need to play something first.")

    @commands.command()
    async def resume(self, ctx):
        if not await self.players[ctx.guild.id].resume():
            async with ctx.typing():
                await ctx.send("You need to play something first.")

    @commands.command()
    async def disconnect(self, ctx):
        if not await self.players[ctx.guild.id].disconnect():
            await ctx.send("Not connected to any VC.")

    @commands.command()
    async def next(self, ctx):
        self.players[ctx.guild.id].next()

if __name__ == "__main__":
    client.add_cog(MusicStreamingCog(client))
    client.run(key.bot_key)
