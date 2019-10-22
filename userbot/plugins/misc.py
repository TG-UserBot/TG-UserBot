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
import requests
from datetime import datetime
from functools import partial
from PIL import Image
from telethon.utils import get_extension

from userbot import client, LOGGER
from userbot.utils.helpers import restart as shell_restart


@client.onMessage(
    command="ping", info="Get message ping",
    outgoing=True, regex="ping$"
)
async def ping(event):
    """Ping function used to edit the message for .ping"""
    start = datetime.now()
    await event.edit("**PONG**")
    duration = (datetime.now() - start)
    milliseconds = duration.microseconds / 1000
    await event.edit(f"**PONG**\n`{milliseconds}ms`")


@client.onMessage(
    command="resetprefix", info="Forgot your prefix? This resets to default.",
    outgoing=True, regex=r"(?i)^resetprefix$", disable_prefix=True
)
async def resetprefix(event):
    """Reset your prefix to the default ones."""
    prefix = event.client.config['userbot'].get('prefix', None)
    if prefix:
        del client.config['userbot']['prefix']
        event.client.prefix = None
        await event.edit(
            "`Succesffully reset your prefix to the deafult ones!`"
        )
        client._updateconfig()
    else:
        await event.edit(
            "`There is no prefix set as a default!`"
        )


@client.onMessage(
    command="setprefix", info="Change the current prefix of commands.",
    outgoing=True, regex=r"setprefix (.+)"
)
async def setprefix(event):
    """Change the prefix default prefix."""
    match = event.matches[0].group(1).strip()
    old_prefix = client.prefix
    event.client.prefix = match
    event.client.config['userbot']['prefix'] = match
    if old_prefix is None:
        await event.edit(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**resetprefix**".format(event.client.prefix)
        )
    else:
        await event.edit(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**{0}setprefix {1}**".format(
                event.client.prefix, old_prefix
            )
        )
    client._updateconfig()


@client.onMessage(
    command="shutdown", info="Disconnect the client and exit the script.",
    outgoing=True, regex="shutdown$", builtin=True
)
async def shutdown(event):
    """Shutdown userbot."""
    await event.edit("`Disconnecting the client and exiting. Ciao!`")
    print()
    LOGGER.info("Disconnecting the client and exiting the main script.")
    await event.client.disconnect()


@client.onMessage(
    command="restart", info="Restart (the client and reimport plugins).",
    outgoing=True, regex="restart(?: |$)(client)?$", builtin=True
)
async def restart(event):
    """Restart userbot."""
    arg = event.matches[0].group(1)
    if arg:
        event.client.loop.create_task(event.client._restarter(event))
    else:
        await event.edit("`BRB disconnecting and starting the script again!`")
        await shell_restart(event)


@client.onMessage(
    command="enable", info="Enable a disabled command.",
    outgoing=True, regex=r"enable (\w+)$", builtin=True
)
async def enable(event):
    command = event.matches[0].group(1)
    if event.client.disabled_commands.get(command, False):
        com = event.client.disabled_commands.get(command)
        for handler in com.handlers:
            event.client.add_event_handler(com.func, handler)
        event.client.commands.update({command: com})
        del event.client.disabled_commands[command]
        await event.edit(f"`Successfully enabled {command}`")
    else:
        await event.edit(
            "`Couldn't find the specified command. "
            "Perhaps it's not disabled?`"
        )


@client.onMessage(
    command="disable", info="Disable an enabled command.",
    outgoing=True, regex=r"disable (\w+)$", builtin=True
)
async def disable(event):
    command = event.matches[0].group(1)
    if event.client.commands.get(command, False):
        com = event.client.commands.get(command)
        if com.builtin:
            await event.edit("`Cannot disable a builtin command.`")
        else:
            event.client.remove_event_handler(com.func)
            event.client.disabled_commands.update({command: com})
            del event.client.commands[command]
            await event.edit(f"`Successfully disabled {command}`")
    else:
        await event.edit("`Couldn't find the specified command.`")


@client.onMessage(
    command="commands", info="Lists all the enabled commands.",
    outgoing=True, regex="commands$", builtin=True
)
async def commands(event):
    response = "**Enabled commands:**"
    for name, command in sorted(event.client.commands.items()):
        response += f"\n**{name}:** `{command.info}`"
    await event.edit(response)


@client.onMessage(
    command="disabled", info="Lists all the disabled commands.",
    outgoing=True, regex="disabled$", builtin=True
)
async def disabled(event):
    disabled_commands = event.client.disabled_commands

    if not disabled_commands:
        await event.edit("`There are no disabled commands currently.`")
        return

    response = "**Disabled commands:**"
    for name, command in disabled_commands.items():
        response += f"\n**{name}:** `{command.info}`"
    await event.edit(response)


@client.onMessage(
    command="rmbg", info="Remove the background of an image.",
    outgoing=True, regex="rmbg(?: |$)(.*)$"
)
async def rmbg(event):
    API_KEY = client.config['api_keys'].get('api_key_removebg', False)
    if not API_KEY:
        await event.edit("`You don't have an API key set for remove.bg!`")
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
                        await event.edit(
                            "`The provided link seems to be invalid.`"
                        )
                        return
            except aiohttp.client_exceptions.InvalidURL:
                await event.edit("`Invalid URL provided!`")
                return
            except Exception as e:
                await event.edit(f"`Unknown exception: {e}`")
                return
        media = match
    elif reply and reply.media:
        ext = get_extension(reply.media)
        acceptable = [".jpg", ".png", ".bmp", ".tif", ".webp"]
        if ext not in acceptable:
            await event.edit("`Nice try, fool!`")
            return

        await event.edit("`Downloading media...`")
        media = io.BytesIO()
        await client.download_media(reply, media)
        if ext in [".bmp", ".tif", ".webp"]:
            media.seek(0)
            new_media = io.BytesIO()
            pilImg = Image.open(media)
            pilImg.save(new_media, format="PNG")
            pilImg.close()
            media.close()
            media = new_media
    else:
        await event.edit("`Reply to a photo or provide a valid link.`")
        return

    response = await client.loop.run_in_executor(
        None, partial(removebg_post, API_KEY, media)
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
        await event.edit(text)


def removebg_post(API_KEY: str, media: io.BytesIO or str):
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
