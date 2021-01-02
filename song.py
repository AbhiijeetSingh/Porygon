from types import coroutine
import discord


class Song(object):
    def __init__(self,
                 voice_client: discord.VoiceClient,
                 title: str,
                 source: discord.FFmpegPCMAudio,
                 send_func: coroutine,
                 requested_by_mention:str) -> None:

        self.voice_client = voice_client
        self.title = title
        self.source = source
        self.send_func = send_func
        self.requested_by_mention = requested_by_mention
