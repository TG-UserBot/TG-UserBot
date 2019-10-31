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
import io
import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from urllib import request
from telethon.utils import get_extension

from userbot import client
from userbot.utils.helpers import get_chat_link


opener = request.build_opener()
loop = client.loop
light_useragent = """Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/\
MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 \
Mobile Safari/537.36"""

heavy_useragent = """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"""


@client.onMessage(
    command="reverse", info="Reverse search images on Google",
    outgoing=True, regex=r"reverse(?: |$)(\d*)"
)
async def reverse(event):
    """Reverse search supported media types on Google images."""

    reply = await event.get_reply_message()
    if reply and reply.media:
        ext = get_extension(reply.media)
        acceptable = [".jpg", ".gif", ".png", ".bmp", ".tif", ".webp"]
        if ext not in acceptable:
            await event.answer("`Nice try, fool!`")
            return

        await event.answer("`Downloading media...`")
        photo = io.BytesIO()
        await client.download_media(reply, photo)
    else:
        await event.answer("`Reply to a photo or a non-animated sticker.`")
        return

    photo.seek(0)
    name = "media" + ext

    response = await _run_sync(partial(_post, name, photo))

    fetchUrl = response.headers['Location']
    photo.close()

    if not response.ok:
        await event.answer("`Google told me to go away!`")
        return

    match = await _scrape_url(fetchUrl + "&hl=en")
    guess = match['best_guess']
    imgspage = match['similar_images']
    matching_text = match['matching_text']
    matching = match['matching']

    if guess and imgspage:
        text = (
            f"[{guess}]({fetchUrl})\n\n[Visually similar images]({imgspage})"
        )
        if matching_text and matching:
            text += "\n\n**" + matching_text + ":**"
            for title, link in matching.items():
                text += f"\n[{title.strip()}]({link.strip()})"
        msg = await get_chat_link(event, event.id)
        extra = f"Successfully reversed media in {msg}: [{guess}]({fetchUrl})"
        await event.answer(text, log=("reverse", extra))
    else:
        await event.answer("`Couldn't find anything for you.`")
        return

    limit = event.matches[0].group(1)
    lim = int(limit) if limit else 2

    images = await _get_similar_links(imgspage, lim)
    if images:
        await client.send_file(
            entity=await event.get_input_chat(),
            file=images,
            reply_to=event.message.id
        )


def _post(name: str, media: io.BytesIO):
    searchUrl = 'https://www.google.com/searchbyimage/upload'
    multipart = {'encoded_image': (name, media), 'image_content': ''}

    response = requests.post(
        searchUrl,
        files=multipart,
        allow_redirects=False
    )

    return response


async def _scrape_url(googleurl):
    """Parse/Scrape the HTML code for the info we want."""

    opener.addheaders = [('User-agent', heavy_useragent)]

    source = await _run_sync(partial(opener.open, googleurl))
    soup = BeautifulSoup(source.read(), 'html.parser')

    result = {
        'similar_images': '',
        'best_guess': '',
        'matching_text': '',
        'matching': {}
    }

    first = "div", {'class': 'med', 'id': 'res', 'role': 'main'}
    second = "div", {'id': 'topstuff'}
    third = "div", {'class': 'r5a77d'}
    fourth = "div", {'id': 'search'}
    fifth = 'a', {'class': 'iu-card-header'}
    sixth = "div", {'class': 'rg-header V5niGc dPAwzb'}
    seventh = "div", {'class': 'bkWMgd'}
    eighth = 'a', {'href': True, 'ping': True}

    for main in soup.findAll(*first):
        for related in main.find(*second).findAll(*third):
            result['best_guess'] = related.get_text()

        for search in main.find(*fourth):
            for similar_image in search.findAll(*fifth):
                result['similar_images'] = (
                    "https://www.google.com" + similar_image.get('href')
                    )

            for match_text in search.findAll(*sixth):
                result['matching_text'] = match_text.get_text()

            for match in search.findAll(*seventh)[-1]:
                for links in match.findAll(*eighth):
                    if len(links.attrs) == 2:
                        result['matching'].update(
                            {links.h3.get_text(): links.get('href')}
                        )

    return result


async def _get_similar_links(link: str, lim: int = 2):
    """Parse/Scrape the HTML code for the info we want."""

    opener.addheaders = [('User-agent', light_useragent)]

    source = await _run_sync(partial(opener.open, link))

    links = []
    counter = 0

    pattern = (
        r",\[\"(.*\.(?:png|jpg|jpeg|bmp|svg\+xml|webp|gif))\",[0-9]+,[0-9]+\]"
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
                    links.append(await response.read())
            if counter >= int(lim):
                break

    return links


async def _run_sync(func: callable):
    return await loop.run_in_executor(ThreadPoolExecutor(), func)
