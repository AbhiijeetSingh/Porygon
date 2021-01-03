from types import coroutine
import discord


class Song(object):
    def __init__(self,
                 title: str,
                 source: str,
                 context: discord.ext.commands.Context,
                 ) -> None:

        self.title = title
        self.source = source
        self.ctx = context
