# entries 0 webpage_url
# entries 0 id
from asyncio import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
from youtube_dl import YoutubeDL
import discord


BASE_PATH = "PorygonSongs" 

async def extract_info_from_yt(query):
    with ThreadPoolExecutor(1) as pool:
        event_loop = asyncio.get_event_loop()
        with YoutubeDL({"noplaylist": "True"}) as yt_dl:
            info = await event_loop.run_in_executor(pool, yt_dl.extract_info(f"ytsearch:{query}"))
    return info 

def is_cached(filename):
    return os.path.exists(os.path.join(BASE_PATH, filename))

async def _download(webpage_url):
    with ThreadPoolExecutor(1) as pool:
        event_loop = asyncio.get_event_loop()
        await event_loop.run_in_executor(pool, subprocess.run(
            f'youtube-dl {webpage_url} -f bestaudio -o "{BASE_PATH}\\%(id)"'
        ))

class AudioRepo(object):
    def __init__(self):
        try:
            os.makedirs(BASE_PATH)
        except FileExistsError:
            pass

    async def get(self, query):
        info = await extract_info_from_yt(query)
        id = info['entries'][0]['id']
        if is_cached(id):
            pass
        else:
            await _download(info['entries'][0]['webpage_url'])
        return discord.FFmpegPCMAudio(source=os.path.join(BASE_PATH, id))