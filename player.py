import asyncio
import discord


class Player(object):
    def __init__(self, queue):
        self.queue = queue
        self.skip = False
        self.voice_client = None
        self._loop = False

    async def start(self):
        while True:
            song = await self.queue.get()
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
            self.voice_client.play(discord.FFmpegPCMAudio(source=song.source))

            if self._loop:
                await self.queue.put(song)

            while self.voice_client.is_playing() or self.voice_client.is_paused():
                if self.skip:
                    self.skip = False
                    break
                await asyncio.sleep(0.5)

    async def pause(self, ctx):
        if self.voice_client.is_playing():
            self.voice_client.pause()
            await ctx.message.add_reaction('\U000023F8')

    async def resume(self, ctx):
        if not self.voice_client.is_playing():
            self.voice_client.resume()
            await ctx.message.add_reaction('\U000025B6')
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
            await ctx.message.add_reaction('\U0001F50C')
        else:
            await ctx.send("Porygon is not connnected")

    async def next(self, ctx):
        self.skip = True
        await ctx.message.add_reaction('\U000023ED')

    async def add_to_queue(self, item):
        await self.queue.put(item)

    def get_queue_length(self):
        q_size = self.queue.qsize()
        if self.voice_client:
            return q_size + 1 if self.voice_client.is_playing() else q_size
        else:
            return q_size

    async def loop_queue(self, ctx):
        # Toggles queue looping.
        self._loop = not self._loop

        title = "Now looping." if self._loop else "Looping now disabled."
        embed = discord.Embed(
            title=title,
            color=0x00DAFF
        )
        await ctx.message.add_reaction("\U0001F501")
        await ctx.send(embed=embed)

    async def queue_list(self, ctx):
        song_names=''
        
        for index in range(self.queue.qsize()):
            song = await self.queue.get()
            song_names+=f"{index+1}. {song.title}\n"
            await self.queue.put(song)
        
        embed = discord.Embed(
            title="Queue",
            description=song_names,
            color = 0x00DAFF
        )
        await ctx.message.add_reaction("\U0001F4C3")
        await ctx.send(embed=embed)

