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
from userbot.helper_funcs import misc
from userbot.utils.helpers import get_chat_link, restart
from userbot.utils.events import NewMessage


plugin_category = "misc"
invite_links = {
    'private': re.compile(r'^(?:https?://)?(t\.me/joinchat/\w+)/?$'),
    'public': re.compile(r'^(?:https?://)?t\.me/(\w+)/?$'),
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
    """Resolve an invite link or a username."""
    link = event.matches[0].group(1)
    if not link:
        await event.answer("`Resolved the void.`")
        return
    text = f"`Couldn't resolve:` {link}"
    for link_type, pattern in invite_links.items():
        match = pattern.match(link)
        if match is not None:
            valid = match.group(1)
            if link_type == "private":
                creatorid, cid, _ = utils.resolve_invite_link(valid)
                if not cid:
                    await event.answer(text)
                    return
                try:
                    creator = await client.get_entity(creatorid)
                    creator = await get_chat_link(creator)
                except (TabError, ValueError):
                    creator = f"`{creatorid}`"
                text = f"**Link:** {link}"
                text += f"\n**Link creator:** {creator}\n**ID:** `{cid}`"
                try:
                    chat = await client.get_entity(cid)
                except (TypeError, ValueError):
                    break

                if isinstance(chat, types.Channel):
                    result = await client(
                        functions.channels.GetFullChannelRequest(
                            channel=chat
                        )
                    )
                    text += await misc.resolve_channel(event.client, result)
                elif isinstance(chat, types.Chat):
                    result = await client(
                        functions.messages.GetFullChatRequest(
                            chat_id=chat
                        )
                    )
                    text += await misc.resolve_chat(event.client, result)
                break
            else:
                try:
                    chat = await client.get_entity(valid)
                except (TypeError, ValueError):
                    continue

                if isinstance(chat, types.User):
                    text = f"**ID:** `{chat.id}`"
                    if chat.username:
                        text += f"\n**Username:** @{chat.username}"
                    text += f"\n{await get_chat_link(chat)}"

                if isinstance(chat, types.ChatForbidden):
                    text += f"\n`Not allowed to view {chat.title}.`"
                elif isinstance(chat, types.ChatEmpty):
                    text += "\n`The chat is empty.`"
                elif isinstance(chat, types.Chat):
                    text = f"**Chat:** @{valid}"
                    result = await client(
                        functions.messages.GetFullChatRequest(
                            chat_id=chat
                        )
                    )
                    text += await misc.resolve_chat(event.client, result)

                if isinstance(chat, types.ChannelForbidden):
                    text += f"\n`Not allowed to view {chat.title}.`"
                elif isinstance(chat, types.Channel):
                    text = f"**Channel:** @{valid}"
                    result = await client(
                        functions.channels.GetFullChannelRequest(
                            channel=chat
                        )
                    )
                    text += await misc.resolve_channel(event.client, result)
    await event.answer(text, link_preview=False)


@client.onMessage(
    command=("mention", plugin_category),
    outgoing=True, regex=r"mention(?: |$)(@?\w{5,32}|\d+)?(?: |$)(.*)$"
)
async def bot_mention(event: NewMessage.Event) -> None:
    """Mention a user in the bot like link with a custom name."""
    user = event.matches[0].group(1)
    name = event.matches[0].group(2)
    if not (user and name):
        await event.answer("`Mentioned the void.`")
        return

    try:
        user = await client.get_input_entity(user)
    except (TypeError, ValueError):
        await event.answer("`Couldn't get the entity.`")
        return

    if not isinstance(user, types.InputPeerUser):
        await event.answer("`Cannot mention non-users.`")
        return
    text = f"[{name}](tg://user?id={user.user_id})"
    await event.answer(text)
