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


import concurrent

from userbot import client, LOGGER
from userbot.utils.helpers import is_ffmpeg_there
from userbot.helper_funcs.yt_dl import (
    extract_info, hook, list_formats, YTdlLogger
)


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

ydl_opts = {
    'logger': YTdlLogger(),
    'progress_hooks': [hook],
    'postprocessors': [],
    'restrictfilenames': True,
    'outtmpl': 'YT_DL/%(title)s_{time}.%(ext)s',
    'prefer_ffmpeg': True,
    'geo_bypass': True,
    'nocheckcertificate': True,
    'logtostderr': False,
    'quiet': True
}

ffurl = (
    "https://tg-userbot.readthedocs.io/en/latest/"
    "faq.html#how-to-install-ffmpeg"
)

async def upload_progress(current, total):
    """ Logs the upload progress """
    LOGGER.info(f"Uploaded {current} of {total} bytes.\
    \nProgress: {(current / total) * 100}%")

@client.onMessage(
    command="ytdl",
    outgoing=True, regex=r"ytdl(?: |$)(.+?)?(?: |$)(.+)?$"
)
async def yt_dl(event):
    """Download videos from YouTube with their url in multiple formats."""
    url = event.matches[0].group(1)
    fmt = event.matches[0].group(2)
    if not url:
        await event.answer("`.ytdl <url>` or `.ytdl <url> <format>`")
        return

    ffmpeg = await is_ffmpeg_there()
    params = ydl_opts.copy()

    if fmt:
        fmt = fmt.strip()
        if fmt == 'listformats':
            info = await extract_info(
                client.loop, concurrent.futures.ThreadPoolExecutor(),
                params, url
            )
            if isinstance(info, dict):
                fmts = await list_formats(info)
                await event.answer(fmts)
            else:
                await event.answer(info)
            return
        elif fmt in audioFormats and ffmpeg:
            params.update({'format': 'bestaudio'})
            params['postprocessors'].append(
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': fmt,
                    'preferredquality': '320',
                }
            )
        elif fmt in videoFormats and ffmpeg:
            params.update({'format': 'bestvideo'})
            params['postprocessors'].append(
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': fmt
                }
            )
        else:
            params.update({'format': fmt})
            if ffmpeg:
                params.update({'key': 'FFmpegMetadata'})
                if fmt in ['mp3', 'mp4', 'm4a']:
                    params.update({'writethumbnail': True})
                    params['postprocessors'].append({'key': 'EmbedThumbnail'})

    await event.answer("`Processing...`")
    output = await extract_info(
        client.loop, concurrent.futures.ThreadPoolExecutor(),
        params, url, download=True
    )
    warning = (
        f"`WARNING: FFMPEG is not installed!` [FFMPEG install guide]({ffurl})"
        " `If you requested multiple formats, they won't be merged.`\n\n"
    )
    if isinstance(output, str):
        result = warning + output if not ffmpeg else output
        await event.answer(result, link_preview=False)
    else:
        text, title, link, path = output
        huh = f"[{title}]({link})"
        result = warning + text if not ffmpeg else text
        await event.answer(f"`Uploading` {huh}`...`", link_preview=False)
        await client.send_file(
            event.chat_id, path, force_document=True, progress_callback=upload_progress, reply_to=event
        )
        await event.answer(
            result, log=("YTDL", f"Successfully downloaded {huh}!")
        )
