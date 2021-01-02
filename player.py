import asyncio

import discord


class Player(object):
    def __init__(self, queue):
        self.queue = queue
        self.skip = False
        self.voice_client = None

    async def start(self):
        while True:
            song = await self.queue.get()
            self.voice_client = song.voice_client

            self.voice_client.stop() if self.voice_client.is_playing(
            ) or self.voice_client.is_paused() else None

            embed = discord.Embed(
                title="Now playing",
                description=song.title,
                color=0x00DAFF
            ).add_field(name="Requested by", value=song.requested_by_mention)

            await song.send_func(
                embed=embed
            )

            self.voice_client.play(song.source)
            while self.voice_client.is_playing() or self.voice_client.is_paused():
                if self.skip:
                    self.skip = False
                    break
                await asyncio.sleep(0.5)

    async def pause(self):
        if self.voice_client.is_playing():
            self.voice_client.pause()
            return True
        else:
            return False

    async def resume(self):
        if not self.voice_client.is_playing():
            self.voice_client.resume()
            return True
        else:
            return False

    async def disconnect(self):
        # If bot is connected to the voice channel
        # the it disconnects and returns True, otherwise
        # returns False
        if self.voice_client.is_connected():
            for _ in range(self.queue.qsize()):
                self.queue.get_nowait()
            await self.voice_client.disconnect()
            return True
        else:
            return False

    def next(self):
        self.skip = True

    async def add_to_queue(self, item):
        await self.queue.put(item)

    def get_queue_length(self):
        q_size = self.queue.qsize()
        if self.voice_client:
            return q_size + 1 if self.voice_client.is_playing() else q_size
        else:
            return q_size
