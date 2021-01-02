import asyncio

import discord


class Player(object):
    def __init__(self, queue):
        self.queue = queue
        self.skip = False
        self.voice_client = None
        self.loop = False

    async def start(self):
        while True:
            song = await self.queue.get()
            if self.loop:
                await self.queue.put(song)
            self.voice_client = song.ctx.voice_client

            self.voice_client.stop() if self.voice_client.is_playing(
            ) or self.voice_client.is_paused() else None

            embed = discord.Embed(
                title="Now playing",
                description=song.title,
                color=0x00DAFF
            ).add_field(name="Requested by", value=song.ctx.author.mention)

            await song.ctx.send(
                embed=embed
            )

            self.voice_client.play(song.source)
            while self.voice_client.is_playing() or self.voice_client.is_paused():
                if self.skip:
                    self.skip = False
                    break
                await asyncio.sleep(0.5)

    async def pause(self, ctx):
        if self.voice_client.is_playing():
            self.voice_client.pause()
            await ctx.message.add_reaction('\N{PAUSE BUTTON}')

    async def resume(self, ctx):
        if not self.voice_client.is_playing():
            self.voice_client.resume()
            await ctx.message.add_reaction('\N{PLAY BUTTON}')
        else:
            await ctx.send("Nothing is being played")

    async def disconnect(self, ctx):
        # If bot is connected to the voice channel
        # the it disconnects and returns True, otherwise
        # returns False
        if self.voice_client.is_connected():
            for _ in range(self.queue.qsize()):
                self.queue.get_nowait()
            await self.voice_client.disconnect()
            await ctx.message.add_reaction('\N{ELECTRIC PLUG}')
            #await ctx.message.add_reaction('\N{WAVING HAND}')
        else:
            await ctx.send("Porygon is not connnected")

    async def next(self, ctx):
        self.skip = True
        await ctx.message.add_reaction('\N{NEXT TRACK BUTTION}')

    async def add_to_queue(self, item):
        await self.queue.put(item)

    def get_queue_length(self):
        q_size = self.queue.qsize()
        if self.voice_client:
            return q_size + 1 if self.voice_client.is_playing() else q_size
        else:
            return q_size

    async def loop(self, ctx):
        # Toggles queue looping.
        self.loop = not self.loop

        title = "Now looping." if self.loop else "Looping now disabled."
        embed = discord.Embed(
            title=title,
            color=0x00DAFF
        )
        # await ctx.message.add_reaction("\N{REPEAT BUTTON}")
        await ctx.send(embed=embed)
