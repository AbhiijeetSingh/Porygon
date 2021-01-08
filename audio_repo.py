# To download the get the
# song query passed.
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
from youtube_dl import YoutubeDL
from databases import Database
from sqlalchemy import Table, Column, MetaData, String
from sqlalchemy.sql import select

BASE_PATH = "PorygonSongs"


async def extract_info_from_yt(query):
    with ThreadPoolExecutor(1) as pool:
        event_loop = asyncio.get_event_loop()
        with YoutubeDL({"format": "bestaudio", "noplaylist": "True"}) as yt_dl:
            info = await event_loop.run_in_executor(pool, yt_dl.extract_info, f"ytsearch:{query}", False)
    return info


def is_cached(filename):
    return os.path.exists(os.path.join(BASE_PATH, filename))


async def _download(webpage_url, filename):
    with ThreadPoolExecutor(1) as pool:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(pool, subprocess.run,
                                   f'youtube-dl -f bestaudio --output {os.path.join(BASE_PATH, filename)} {webpage_url}'
                                   )


def clear_repo():
    song_repo = os.listdir(BASE_PATH)
    while len(song_repo) > 30:
        song_repo = os.listdir(BASE_PATH)
        full_path = [f"{BASE_PATH}/{x}" for x in song_repo]
        oldest_file = min(full_path, key=os.path.getctime)
        os.remove(oldest_file)


class AudioRepo(object):
    def __init__(self):
        try:
            os.makedirs(BASE_PATH)
        except FileExistsError:
            pass
        self.database = Database(f"sqlite:///{BASE_PATH}/audios.db")
        self.metadata = MetaData()
        self.search_results = Table(
            "search_results",
            self.metadata,
            Column("id", String),
            Column("search_text", String),
            Column("title", String),
            Column("thumbnail", String),
            Column("webpage_url", String)
        )

    async def init(self):
        await self.database.connect()

    async def clean_up(self):
        await self.database.disconnect()

    async def get_info(self, query):
        query = query.strip().lower()
        db_query = select([self.search_results]).where(
            self.search_results.c.search_text == query)
        result = await self.database.fetch_one(query=db_query)

        if result:
            info = dict(
                id=result.id,
                title=result.title,
                thumbnail=result.thumbnail,
                webpage_url=result.webpage_url
            )
            return info
        else:
            youtube_dl_info = await extract_info_from_yt(query)
            info = dict(
                id=youtube_dl_info['entries'][0]['id'],
                title=youtube_dl_info['entries'][0]['title'],
                thumbnail=youtube_dl_info['entries'][0]['thumbnail'],
                webpage_url=youtube_dl_info['entries'][0]['webpage_url']
            )
            async with self.database.transaction():
                db_query = self.search_results.insert()
                values = dict(search_text=query, **info)
                await self.database.execute(query=db_query, values=values)
            return info

    async def get(self, info):
        id = info['id']
        if is_cached(id):
            pass
        else:
            await _download(info['webpage_url'], info['id'])
        return os.path.join(BASE_PATH, id)
