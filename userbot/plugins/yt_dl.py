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
warning = (
    f"`WARNING: FFMPEG is not installed!` [FFMPEG install guide]({ffurl})"
    " `If you requested multiple formats, they won't be merged.`\n\n"
)
success = "`Successfully downloaded` {}"


@client.onMessage(
    command="ytdl",
    outgoing=True, regex=r"ytdl(?: |$)([\s\S]*)"
)
async def yt_dl(event):
    """Download videos from YouTube with their url in multiple formats."""
    match = event.matches[0].group(1)
    if not match:
        await event.answer(
            "`.ytdl <url>` or `.ytdl <url1> .. <urln> format=<fmt>`"
        )
        return

    args, kwargs = await client.parse_arguments(match)
    fmt = kwargs.get('format', kwargs.get('fmt', False))
    round_message = kwargs.get('round_message', kwargs.get('round', False))
    supports_streaming = kwargs.get(
        'supports_streaming', kwargs.get('stream', False)
    )
    ffmpeg = await is_ffmpeg_there()
    params = copy.deepcopy(ydl_opts)
    warnings = []

    if fmt:
        fmt = fmt.strip().lower()
        if fmt == 'listformats':
            fmts = []
            for url in args:
                info = await extract_info(
                    client.loop, concurrent.futures.ThreadPoolExecutor(),
                    params, url
                )
                if isinstance(info, dict):
                    fmts.append(await list_formats(info))
                else:
                    warnings.append(info)
            if fmts:
                text = "**Formats:**\n"
                text += ",\n\n".join(f"`{f}`" for f in fmts)
                await event.answer(text)
            if warnings:
                text = "**Warnings:**\n"
                text += ",\n\n".join(f"`{w}`" for w in warnings)
                reply = True if fmts else False
                await event.answer(text, reply=reply)
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
    params['progress_hooks'].append(progress.hook)
    progress_cb = ProgressCallback(event)

    for url in args:
        await event.answer(f"`Processing {url}...`")
        output = await extract_info(
            loop=client.loop, ydl_opts=params, url=url, download=True,
            executor=concurrent.futures.ThreadPoolExecutor()
        )
        if isinstance(output, str):
            result = warning + output if not ffmpeg else output
            warnings.append(result)
        else:
            path, thumb, info = output
            title = info.get('title', info.get('id', 'Unknown title'))
            url = info.get('webpage_url', None)
            href = f"[{title}]({url})"
            text = success.format(href)
            result = warning + text if not ffmpeg else text

            dl = io.open(path, 'rb')
            progress_cb.filen = title
            uploaded = await client.fast_upload_file(
                dl, progress_cb.up_progress
            )
            dl.close()

            attributes, mime_type = await fix_attributes(
                path, info, round_message, supports_streaming
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
    if warnings:
        text = "**Warnings:**\n"
        text += ",\n\n".join(f"`{w}`" for w in warnings)
        await event.answer(text)
    else:
        await event.delete()


async def fix_attributes(
    path, info_dict: dict,
    round_message: bool = False, supports_streaming: bool = False
) -> list:
    """Avoid multiple instances of an attribute."""
    new_attributes = []
    video = False
    audio = False

    title = str(info_dict.get('title', info_dict.get('id', 'Unknown title')))
    uploader = info_dict.get('uploader', 'Unknown artist')
    duration = int(info_dict.get('duration', 0))
    suffix = path.suffix[1:]
    if supports_streaming and suffix != 'mp4':
        supports_streaming = False

    attributes, mime_type = get_attributes(path)
    if suffix in audioFormats:
        audio = types.DocumentAttributeAudio(duration, None, title, uploader)
    elif suffix in videoFormats:
        width = int(info_dict.get('width', 0))
        height = int(info_dict.get('height', 0))
        for attr in attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                duration = duration or attr.duration
                width = width or attr.w
                height = height or attr.h
                break
        video = types.DocumentAttributeVideo(
            duration, width, height, round_message, supports_streaming
        )

    for attr in attributes:
        if audio and isinstance(attr, types.DocumentAttributeAudio):
            new_attributes.append(audio)
        elif video and isinstance(attr, types.DocumentAttributeAudio):
            new_attributes.append(video)
        else:
            new_attributes.append(attr)

    return new_attributes, mime_type
