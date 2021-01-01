from concurrent.futures.thread import ThreadPoolExecutor
import subprocess
import discord
from discord import file
from discord.ext import commands
from discord.ext.commands.core import command
from audio_repo import AudioRepo
import key
import asyncio
from youtube_dl import YoutubeDL
from concurrent.futures import ProcessPoolExecutor

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

    @commands.command()
    async def play(self, ctx, *query):
        query = " ".join(query)
        channel = ctx.author.voice.channel if ctx.author.voice else None

        if channel is None:
            async with ctx.typing():
                await ctx.send("Please join a voice channel first.")

        else:
            voice_client = await channel.connect()

            async with ctx.typing():
                await ctx.send(f"Now playing")

            source = await self.audio_repo.get(query)
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

    @commands.command()
    async def stop(self, ctx):
        if ctx.guild.id in self.voice_clients:
            await self.voice_clients.get(ctx.guild.id).disconnect()
        else:
            pass


client.add_cog(MusicStreamingCog(client))
client.run(key.bot_key)
