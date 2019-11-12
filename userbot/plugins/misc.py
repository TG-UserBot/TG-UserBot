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
import functools
import io
import PIL
import requests
from typing import BinaryIO

from telethon.utils import get_extension

from userbot import client, LOGGER
from userbot.utils.helpers import restart as shell_restart
from userbot.utils.events import NewMessage


plugin_category = "misc"


@client.onMessage(
    command=("shutdown", plugin_category),
    outgoing=True, regex="shutdown$", builtin=True
)
async def shutdown(event: NewMessage.Event) -> None:
    """Shutdown the userbot script."""
    await event.answer("`Disconnecting the client and exiting. Ciao!`")
    client.reconnect = False
    print()
    LOGGER.info("Disconnecting the client and exiting the main script.")
    await client.disconnect()


@client.onMessage(
    command=("restart", plugin_category),
    outgoing=True, regex="restart$", builtin=True
)
async def restart(event: NewMessage.Event) -> None:
    """Restart the userbot script."""
    await event.answer(
        "`BRB disconnecting and starting the script again!`",
        log=("restart", "Restarted the userbot script")
    )
    await shell_restart(event)


@client.onMessage(
    command=("rmbg", plugin_category),
    outgoing=True, regex="rmbg(?: |$)(.*)$"
)
async def rmbg(event: NewMessage.Event) -> None:
    """Remove the background from an image or sticker."""
    API_KEY = client.config['api_keys'].get('api_key_removebg', False)
    if not API_KEY:
        await event.answer("`You don't have an API key set for remove.bg!`")
        return

    match = event.matches[0].group(1)
    reply = await event.get_reply_message()

    if match and match != '':
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(match) as response:
                    if not (
                        response.status == 200 and
                        response.content_type.startswith('image/')
                    ):
                        await event.answer(
                            "`The provided link seems to be invalid.`"
                        )
                        return
            except aiohttp.client_exceptions.InvalidURL:
                await event.answer("`Invalid URL provided!`")
                return
            except Exception as e:
                await event.answer(f"`Unknown exception: {e}`")
                return
        media = match
    elif reply and reply.media:
        ext = get_extension(reply.media)
        acceptable = [".jpg", ".png", ".bmp", ".tif", ".webp"]
        if ext not in acceptable:
            await event.answer("`Nice try, fool!`")
            return

        await event.answer("`Downloading media...`")
        media = io.BytesIO()
        await client.download_media(reply, media)
        if ext in [".bmp", ".tif", ".webp"]:
            media.seek(0)
            new_media = io.BytesIO()
            pilImg = PIL.Image.open(media)
            pilImg.save(new_media, format="PNG")
            pilImg.close()
            media.close()
            media = new_media
    else:
        await event.answer("`Reply to a photo or provide a valid link.`")
        return

    response = await client.loop.run_in_executor(
        None, functools.partial(removebg_post, API_KEY, media)
    )
    if not isinstance(media, str):
        media.close()
    if response.status_code == requests.codes.ok:
        await event.delete()
        image = io.BytesIO(response.content)
        image.name = "image.png"
        await event.respond(file=image, force_document=True)
        image.close()
    else:
        error = response.json()['errors'][0]
        code = error.get('code', False)
        title = error.get('title', 'No title?')
        body = code + ': ' + title if code else title
        text = f"`[{response.status_code}] {body}`"
        await event.answer(text)


def removebg_post(API_KEY: str, media: BinaryIO or str):
    image_parameter = 'image_url' if isinstance(media, str) else 'image_file'
    if not isinstance(media, str):
        media.seek(0)

    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={image_parameter: media},
        data={'size': 'auto'},
        headers={'X-Api-Key': API_KEY},
    )
    return response
