# TG-UserBot - A modular Telegram UserBot script for Python.
# Copyright (C) 2019  Kandarp <https://github.com/kandnub>
#
# TG-UserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TG-UserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TG-UserBot.  If not, see <https://www.gnu.org/licenses/>.


import subprocess
from concurrent.futures import ThreadPoolExecutor

from userbot.events import basic_command, commands
from userbot.helper_funcs.yt_dl import (
    extract_info, hook, list_formats, YTdlLogger
)


executor = ThreadPoolExecutor()

audioFormats = [
    "aac",
    "flac",
    "mp3",
    "m4a",
    "opus",
    "vorbis",
    "wav"
]

videoFormats = [
    "mp4",
    "flv",
    "ogg",
    "webm",
    "mkv",
    "avi"
]

params = {
    'logger': YTdlLogger(),
    'progress_hooks': [hook],
    'postprocessors': [],
    'outtmpl': '%(title)s.%(ext)s',
    'prefer_ffmpeg': True,
    'geo_bypass': True,
    'nocheckcertificate': True,
    'logtostderr': False,
    'quiet': True
}

try:
    subprocess.Popen(
        ['ffmpeg'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    ffmpeg = True
except OSError:
    ffmpeg = False


@commands("ytdl")
@basic_command(command=r"yt_dl (.+?)(?: |$)(.+)?$")
async def yt_dl(client, event):
    """YouTube-DL function used to download videos for .yt_dl"""
    match = event.matches[0]
    url = match.group(1)
    fmt = match.group(2)

    if fmt:
        fmt = fmt.strip()
        if fmt == 'listformats':
            info = await extract_info(executor, params, url)
            if isinstance(info, dict):
                fmts = await list_formats(info)
                await event.edit(fmts)
            else:
                await event.edit(info)
            return
        elif fmt in audioFormats and ffmpeg is True:
            params.update({'format': 'bestaudio'})
            params['postprocessors'].append(
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': fmt,
                    'preferredquality': '320',
                }
            )
        elif fmt in videoFormats and ffmpeg is True:
            params.update({'format': 'bestvideo'})
            params['postprocessors'].append(
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': fmt
                }
            )
        else:
            params.update({'format': fmt})
            if ffmpeg is True:
                params.update({'key': 'FFmpegMetadata'})
                if fmt in ['mp3', 'mp4', 'm4a']:
                    params.update({'writethumbnail': True})
                    params['postprocessors'].append({'key': 'EmbedThumbnail'})

    await event.edit("`Processing...`")
    output = await extract_info(executor, params, url, download=True)
    warning = (
        "`WARNING: FFMPEG is not installed!`"
        " `If you requested multiple formats, they won't be merged.`\n\n"
    )
    result = warning + output if ffmpeg is False else output
    await event.edit(result)
