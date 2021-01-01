import asyncio


class Player(object):
    def __init__(self, queue):
        self.queue = queue
        self.skip = False

    async def start(self):
        while True:
            source, self.voice_client = await self.queue.get()

            self.voice_client.stop() if self.voice_client.is_playing() or self.voice_client.is_paused() else None
            
            self.voice_client.play(source)
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
            await self.voice_client.disconnect()
            return True
        else:
            return False

    def next(self):
        self.skip = True

    async def add_to_queue(self, item):
        await self.queue.put(item)

    def get_queue_length(self):
        return self.queue.qsize()
