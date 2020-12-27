# This is a addon module to help download songs from
# the discord bot, Porygon.

import os


def song_download(link):
    # Downloads songs via link
    command = f"youtube-dl -o DL_songs/%(title)s.%(ext)s -x --audio-format mp3 {link}"
    return os.system(command)


def search_download(usersearch):
    # Downloads songs via searching the most relevant one in the ytsearch.
    command = str(
        r'youtube-dl -x --audio-format mp3 -o DL_songs/%(title)s.%(ext)s ytsearch:"' + usersearch + r'"')
    return os.system(command)
