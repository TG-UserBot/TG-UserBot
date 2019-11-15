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
import re
import requests

from telethon import utils
from telethon.tl import functions, types

from userbot import client, LOGGER
from userbot.utils.helpers import get_chat_link, get_entity_info, restart
from userbot.utils.events import NewMessage


plugin_category = "misc"
invite_links = {
    'private': re.compile(r'^(?:https://)?(t\.me/joinchat/\w+)/?$'),
    'public': re.compile(r'^(?:https://)?t\.me/(\w+)/?$'),
    'username': re.compile(r'^@?(\w{5,32})$')
}


def removebg_post(API_KEY: str, media: bytes or str):
    image_parameter = 'image_url' if isinstance(media, str) else 'image_file'
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={image_parameter: media},
        data={'size': 'auto'},
        headers={'X-Api-Key': API_KEY},
    )
    return response


async def unparse_info(creator, admins, bots, users, kicked, banned) -> str:
    text = ''
    if creator:
        c = await client.get_entity(creator)
        text += f"\n**Creator:** {await get_chat_link(c)}"
    if users:
        text += f"\n**Participants:** {users}"
    if admins:
        text += f"\n**Admins:** {admins}"
    if bots:
        text += f"\n**Bots:** {bots}"
    if kicked:
        text += f"\n**Kicked:** {kicked}"
    if banned:
        text += f"\n**Banned:** {banned}"
    return text


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
async def restarter(event: NewMessage.Event) -> None:
    """Restart the userbot script."""
    await event.answer(
        "`BRB disconnecting and starting the script again!`",
        log=("restart", "Restarted the userbot script")
    )
    await restart(event)


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
        ext = utils.get_extension(reply.media)
        acceptable = [".jpg", ".png", ".bmp", ".tif", ".webp"]
        if ext not in acceptable:
            await event.answer("`Nice try, fool!`")
            return

        await event.answer("`Downloading media...`")
        media = io.BytesIO()
        await client.download_media(reply, media)
        if ext in [".bmp", ".tif", ".webp"]:
            new_media = io.BytesIO()
            try:
                pilImg = PIL.Image.open(media)
            except OSError as e:
                await event.answer(f'`OSError: {e}`')
                return
            pilImg.save(new_media, format="PNG")
            pilImg.close()
            media.close()
            media = new_media
    else:
        await event.answer("`Reply to a photo or provide a valid link.`")
        return

    response = await client.loop.run_in_executor(
        None, functools.partial(removebg_post, API_KEY, media.getvalue())
    )
    if not isinstance(media, str):
        media.close()
    if response.status_code == requests.codes.ok:
        await event.delete()
        image = io.BytesIO(response.content)
        image.name = "image.png"
        await event.respond(file=image, force_document=True, reply=True)
        image.close()
    else:
        error = response.json()['errors'][0]
        code = error.get('code', False)
        title = error.get('title', 'No title?')
        body = code + ': ' + title if code else title
        text = f"`[{response.status_code}] {body}`"
        await event.answer(text)


@client.onMessage(
    command=("resolve", plugin_category),
    outgoing=True, regex="resolve(?: |$)(.*)$"
)
async def resolver(event: NewMessage.Event) -> None:
    """Resolve an invite link or username."""
    link = event.matches[0].group(1)
    if not link:
        await event.answer("`Resolving the void.`")
        return
    text = f"`Couldn't resolve:` {link}."
    for link_type, pattern in invite_links.items():
        match = pattern.match(link)
        if match is not None:
            valid = match.group(1)
            if link_type == "private":
                creator, cid, _ = utils.resolve_invite_link(valid)
                if not cid:
                    await event.answer(text)
                    return
                creator = await get_chat_link(await client.get_entity(creator))
                text = f"**Link:** {link}"
                text += f"\n**Creator:** {creator}\n**Chat ID:** `{cid}`"
            else:
                try:
                    chat = await client.get_input_entity(valid)
                except (TypeError, ValueError):
                    chat = None
                if isinstance(
                    chat, (types.InputPeerUser, types.InputPeerSelf)
                ):
                    usr = await client.get_entity(valid)
                    text = f"**ID:** {usr.id}"
                    if usr.username:
                        text += f"\n**Username:** @{usr.username}"
                    text += f"\n{await get_chat_link(usr)}"
                elif isinstance(chat, types.InputPeerChat):
                    text = f"**Chat:** @{valid}"
                    result = await client(
                        functions.messages.GetFullChatRequest(
                            chat_id=chat
                        )
                    )
                    if isinstance(result, types.ChatForbidden):
                        text += f"`Not allowed to view {result.title}.`"
                    elif isinstance(result, types.ChatEmpty):
                        text += "`The chat is empty.`"
                    else:
                        text += f"\n**Chat ID:** {result.full_chat.id}"
                        info = await get_entity_info(result)
                        text += await unparse_info(*info)
                elif isinstance(chat, types.InputPeerChannel):
                    text = f"**Channel:** @{valid}"
                    result = await client(
                        functions.channels.GetFullChannelRequest(
                            channel=chat
                        )
                    )
                    if isinstance(result, types.ChannelForbidden):
                        text += f"`Not allowed to view {result.title}.`"
                    else:
                        text += f"\n**Channel ID:** {result.full_chat.id}"
                        info = await get_entity_info(result)
                        text += await unparse_info(*info)
    await event.answer(text)
