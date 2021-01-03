# To download the get the
# song query passed.

import subprocess
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
from youtube_dl import YoutubeDL


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


class AudioRepo(object):
    def __init__(self):
        try:
            os.makedirs(BASE_PATH)
        except FileExistsError:
            pass

    async def get_info(self, query):
        info = await extract_info_from_yt(query)
        return info

    async def get(self, info):
        id = info['entries'][0]['id']
        if is_cached(id):
            pass
        else:
            await _download(info['entries'][0]['webpage_url'], info['entries'][0]['id'])
        return os.path.join(BASE_PATH, id)
