# This is a addon module to help download songs from
# the discord bot, Porygon.

import os
from youtube_dl import YoutubeDL
import requests

def song_download(link):
    # Downloads songs via link
    command = f"youtube-dl -o DL_songs/%(title)s.%(ext)s -x --audio-format mp3 {link}"
    return os.system(command)


def search_download(usersearch):
    # Downloads songs via searching the most relevant one in the ytsearch.
    command = str(
        r'youtube-dl -f bestaudio --extract-audio -o DL_songs/%(title)s.%(ext)s ytsearch:"' + usersearch + r'"')
    return os.system(command)

#Get videos from links or from youtube search
def search_stream(query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
    return (info['title'],info['formats'][0]['url'])


if __name__ == "__main__":
    print(search_stream("castle on the hill"))