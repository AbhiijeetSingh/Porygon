import os


def song_download(link):
    command = f"youtube-dl -o DL_songs/%(title)s.%(ext)s -x --audio-format mp3 {link}"
    return os.system(command)


def search_download(usersearch):
    command = str(
        r'youtube-dl -x --audio-format mp3 -o DL_songs/%(title)s.%(ext)s ytsearch:"' + usersearch + r'"')
    return os.system(command)
