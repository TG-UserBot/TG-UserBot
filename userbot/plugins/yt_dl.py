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
import copy
import io
import os

from telethon.tl import types
from telethon.utils import get_attributes

from userbot import client
from userbot.utils.helpers import is_ffmpeg_there, ProgressCallback
from userbot.helper_funcs.yt_dl import (
    extract_info, list_formats, ProgressHook, YTdlLogger
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
    'progress_hooks': [],
    'postprocessors': [],
    'restrictfilenames': False,
    'outtmpl': 'YT_DL/%(title)s_{time}.%(ext)s',
    'prefer_ffmpeg': True,
    'geo_bypass': True,
    'nocheckcertificate': True,
    'logtostderr': False,
    'quiet': True,
    'embedthumbnail': True,
    'addmetadata': True,
    'writethumbnail': True,
    'ignoreerrors': False,
    'noplaylist': True
}

ffurl = (
    "https://tg-userbot.readthedocs.io/en/latest/"
    "faq.html#how-to-install-ffmpeg"
)
success = "`Successfully downloaded` {}"


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
    params = copy.deepcopy(ydl_opts)

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
            params.update(format='bestaudio')
            params['postprocessors'].append(
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': fmt,
                    'preferredquality': '320',
                }
            )
        elif fmt in videoFormats and ffmpeg:
            params.update(format='bestvideo')
            params['postprocessors'].append(
                {
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': fmt
                }
            )
        else:
            params.update(format=fmt)
            if ffmpeg:
                params.update(key='FFmpegMetadata')
                if fmt in ['mp3', 'mp4', 'm4a']:
                    params.update(writethumbnail=True)
                    params['postprocessors'].append({'key': 'EmbedThumbnail'})

    progress = ProgressHook(event)
    await event.answer("`Processing...`")
    params['progress_hooks'].append(progress.hook)
    output = await extract_info(
        loop=client.loop, executor=concurrent.futures.ThreadPoolExecutor(),
        ydl_opts=params, url=url, download=True
    )
    warning = (
        f"`WARNING: FFMPEG is not installed!` [FFMPEG install guide]({ffurl})"
        " `If you requested multiple formats, they won't be merged.`\n\n"
    )
    if isinstance(output, str):
        result = warning + output if not ffmpeg else output
        await event.answer(result, link_preview=False)
    else:
        path, thumb, info = output
        title = info.get('title', info.get('id', 'Unknown title'))
        uploader = info.get('uploader', None)
        duration = int(info.get('duration', 0))
        width = info.get('width', None)
        height = info.get('height', None)
        url = info.get('webpage_url', None)
        href = f"[{title}]({url})"
        text = success.format(href)
        result = warning + text if not ffmpeg else text

        progress_cb = ProgressCallback(event, filen=title)
        dl = io.open(path, 'rb')
        uploaded = await client.fast_upload_file(dl, progress_cb.up_progress)
        dl.close()

        attributes, mime_type = get_attributes(path)
        if path.suffix[1:] in audioFormats:
            attributes.append(
                types.DocumentAttributeAudio(duration, None, title, uploader)
            )
        elif path.suffix[1:] in videoFormats:
            attributes.append(
                types.DocumentAttributeVideo(duration, width, height)
            )
        media = types.InputMediaUploadedDocument(
            file=uploaded,
            mime_type=mime_type,
            attributes=attributes,
            thumb=await client.upload_file(thumb) if thumb else None
        )

        await client.send_file(
            event.chat_id, media, caption=href, force_document=True
        )
        if thumb:
            os.remove(thumb)
        await event.delete()
