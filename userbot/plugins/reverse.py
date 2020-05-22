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


import aiohttp
import asyncio
import bs4
import concurrent
import functools
import io
import os
import random
import re
import requests
import urllib
import urllib.parse

from telethon.utils import get_extension

from userbot import client
from userbot.utils.helpers import get_chat_link, is_ffmpeg_there
from userbot.utils.events import NewMessage


opener = urllib.request.build_opener()
loop = client.loop
light_useragent = """Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/\
MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 \
Mobile Safari/537.36"""

heavy_ua1 = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"""
heavy_ua2 = """Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"""


@client.onMessage(
    command="reverse", info="Reverse search images on Google",
    outgoing=True, regex=r"reverse(?: |$)(\d*)"
)
async def reverse(event: NewMessage.Event) -> None:
    """
    Reverse search supported media types on Google images.


    `{prefix}reverse` in reply to a media or **{prefix}reverse (results)**
    """
    reply = await event.get_reply_message()
    if reply and reply.media:
        ffmpeg = await is_ffmpeg_there()
        ext = get_extension(reply.media)
        if reply.gif:
            if not ffmpeg:
                await event.answer("`Install FFMPEG to reverse search GIFs.`")
                return
            ext = ".gif"
        if reply.video:
            if not ffmpeg:
                await event.answer(
                    "`Install FFMPEG to reverse search videos.`"
                )
                return
        acceptable = [".jpg", ".gif", ".png", ".bmp", ".tif", ".webp", ".mp4"]
        if ext not in acceptable:
            await event.answer("`Nice try, fool!`")
            return

        await event.answer("`Downloading media...`")
        if (reply.video or reply.gif) and ffmpeg:
            message = f"{event.chat_id}:{event.message.id}"
            await client.download_media(reply, "media.mp4")
            filters = "fps=10,scale=320:-1:flags=lanczos,"
            filters += "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
            process = await asyncio.create_subprocess_shell(
                f'ffmpeg -i media.mp4 -t 25 -vf "{filters}" -loop 0 media.gif',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            client.running_processes[message] = process
            await event.answer("`Converting the mp4 to a gif...`")
            await process.communicate()
            client.running_processes.pop(message)
            photo = io.BytesIO(io.open("media.gif", mode="rb").read())
            os.remove("media.mp4")
            os.remove("media.gif")
        else:
            photo = io.BytesIO()
            await client.download_media(reply, photo)
    else:
        await event.answer("`Reply to a photo or a non-animated sticker.`")
        return

    await event.answer("`Uploading media...`")
    response = await _run_sync(functools.partial(
        _post, f"media{ext}", photo.getvalue()
    ))

    fetchUrl = response.headers['Location']
    photo.close()

    if not response.ok:
        await event.answer("`Google said go away for a while.`")
        return

    await event.answer("`Parsing the results...`")
    match = await _scrape_url(fetchUrl + "&hl=en")
    if isinstance(match, urllib.error.HTTPError):
        await event.answer(f"`{match.code}: {match.reason}`")
        return
    guess = match['best_guess']
    imgspage = match['similar_images']
    matching_text = match['matching_text']
    matching = match['matching']

    if guess:
        text = f"**Possible related search:** [{guess}]({fetchUrl})"
        if imgspage:
            text += f"\n\n[Visually similar images]({imgspage})"
        if matching_text and matching:
            text += "\n\n**" + matching_text + ":**"
            for title, link in matching.items():
                text += f"\n-  [{title}]({link})"
        msg = await get_chat_link(event, event.id)
        extra = f"Successfully reversed media in {msg}: [{guess}]({fetchUrl})"
        await event.answer(text, log=("reverse", extra))
    else:
        await event.answer(f"[Couldn't find anything for you.]({fetchUrl})")
        return

    limit = event.matches[0].group(1)
    lim = int(limit) if limit else 2

    if imgspage:
        images, gifs = await _get_similar_links(imgspage, lim)
        if images:
            await event.answer(
                file=images,
                reply_to=event.message.id
            )
        if gifs:
            for gif in gifs:
                await event.answer(
                    file=gif,
                    reply_to=event.message.id
                )


def _post(name: str, media: io.BytesIO):
    searchUrl = 'https://www.google.com/searchbyimage/upload'
    multipart = {'encoded_image': (name, media), 'image_content': ''}
    headers = {'User-Agent': heavy_ua1}

    response = requests.post(
        searchUrl,
        files=multipart,
        allow_redirects=False,
        headers=headers
    )
    return response


async def _scrape_url(googleurl):
    """Parse/Scrape the HTML code for the info we want."""

    UA = random.choice([heavy_ua1, heavy_ua2])
    opener.addheaders = [('User-Agent', UA)]

    source = await _run_sync(functools.partial(opener.open, googleurl))
    if isinstance(source, urllib.error.HTTPError):
        return source
    soup = bs4.BeautifulSoup(source.read(), 'html.parser')

    result = {
        'similar_images': '',
        'best_guess': '',
        'matching_text': '',
        'matching': {}
    }

    best_guess = soup.find('div', {'class': 'r5a77d'})
    similar_images = soup.find('div', {'class': 'e2BEnf U7izfe'}).find('a')
    matching_text = soup.find(
        'div', {'class': 'rg-header V5niGc dPAwzb', 'role': 'heading'}
    )
    matching = soup.find(
        'div', {'id': 'search'}
    ).find_all('div', {'class': 'g'})

    if best_guess:
        result['best_guess'] = best_guess.a.get_text()

    if similar_images:
        result['similar_images'] = (
            "https://www.google.com" + similar_images.get('href')
        )

    if matching_text:
        result['matching_text'] = matching_text.get_text()

    if matching:
        for tag in matching:
            tmp = tag.find('a', {'href': True, 'ping': True})
            if tmp and len(tmp.attrs) == 2:
                text = tmp.h3.get_text().strip()
                text = text.replace('[', '').replace(']', '')
                link = urllib.parse.quote_plus(
                    tmp.get('href'), safe=":/-&"
                )
                result['matching'][text] = link

    return result


async def _get_similar_links(link: str, lim: int = 2):
    """Parse/Scrape the HTML code for the info we want."""

    opener.addheaders = [('User-Agent', light_useragent)]

    source = await _run_sync(functools.partial(opener.open, link))
    if isinstance(source, urllib.error.HTTPError):
        return source

    links = []
    gifs = []
    counter = 0

    pattern = (
        r',\[\"'
        r'(.*\.(?:png|jpg|jpeg|bmp|svg\+xml|webp|gif))'  # link
        r'.*\"'  # Suffix of the link which isn't needed
        r',[0-9]+,[0-9]+\]'  # Media height and width
    )
    matches = re.findall(pattern, source.read().decode('utf-8'), re.I)

    async with aiohttp.ClientSession() as session:
        for link in matches:
            async with session.get(link) as response:
                if (
                    response.status == 200 and
                    response.content_type.startswith('image/')
                ):
                    counter += 1
                    if response.content_type.endswith('gif'):
                        gifs.append(link)
                    else:
                        links.append(await response.read())
            if counter >= int(lim):
                break

    return links, gifs


async def _run_sync(func: callable):
    try:
        return await loop.run_in_executor(
            concurrent.futures.ThreadPoolExecutor(), func
        )
    except urllib.error.HTTPError as e:
        return e
