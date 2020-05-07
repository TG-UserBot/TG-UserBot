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


import datetime
import io
import logging

from userbot import client, LOGGER, loggingHandler
from userbot.utils.events import NewMessage
from userbot.utils.helpers import restart


@client.onMessage(
    command=('ping', 'www'),
    outgoing=True, regex='ping$', builtin=True
)
async def ping(event: NewMessage.Event) -> None:
    """Check how long it takes to get an update and respond to it."""
    start = datetime.datetime.now()
    await event.answer("**PONG**")
    duration = (datetime.datetime.now() - start)
    milliseconds = duration.microseconds / 1000
    await event.answer(f"**PONG:** `{milliseconds}ms`")


@client.onMessage(
    command=('shutdown', 'misc'),
    outgoing=True, regex='shutdown$', builtin=True
)
async def shutdown(event: NewMessage.Event) -> None:
    """Shutdown the userbot script."""
    await event.answer("`Disconnecting the client and exiting. Ciao!`")
    client.reconnect = False
    print()
    LOGGER.info("Disconnecting the client and exiting the main script.")
    await client.disconnect()


@client.onMessage(
    command=('restart', 'misc'),
    outgoing=True, regex='restart$', builtin=True
)
async def restarter(event: NewMessage.Event) -> None:
    """Restart the userbot script."""
    await event.answer(
        "`BRB disconnecting and starting the script again!`",
        log=("restart", "Restarted the userbot script")
    )
    await restart(event)


@client.onMessage(
    command=('loglevel', 'logging'),
    outgoing=True, regex=r'loglevel(?: |$)(\w*)', builtin=True
)
async def flushLevelChanger(event: NewMessage.Event) -> None:
    """Chnage the default console logger level"""
    match = event.matches[0].group(1)
    if not match:
        level = logging._levelToName.get(loggingHandler.flushLevel, 'N/A')
        await event.answer(
            f'`Current console logging level is set to: {level}`'
        )
        return
    if match.isdigit():
        level = int(match)
        if (level % 10 != 0) or (level > 50) or (level < 0):
            await event.answer('**Invalid log level specified!**')
            return
    else:
        level = logging._nameToLevel.get(match.upper(), None)
        if not level:
            await event.answer('**Invalid log level specified!**')
            return
    loggingHandler.setFlushLevel(level)
    _level = logging._levelToName.get(level, 'INFO')
    client.config['userbot']['console_logger_level'] = _level
    client._updateconfig()
    await event.answer(
        f'`Successfully changed the logging level to: {_level}`',
        log=('logging', f'Changed the console log level tp {_level}')
    )


@client.onMessage(
    command=('logs', 'logging'),
    outgoing=True, regex=r'logs(?: |$)(\d+|\w+)?', builtin=True
)
async def logsDump(event: NewMessage.Event) -> None:
    """Get a text file of all the logs pending in the memory buffer"""
    match = event.matches[0].group(1)
    level = None
    if match:
        if match.isdigit():
            level = int(match)
            if (level % 10 != 0) or (level > 50) or (level < 0):
                await event.answer('**Invalid log level specified!**')
                return
        else:
            level = logging._nameToLevel.get(match.upper(), None)
            if not level:
                await event.answer('**Invalid log level specified!**')
                return
    dump = loggingHandler.dumps(level)
    output = io.BytesIO('\n'.join(dump).encode())
    output.name = "logs.txt"
    await event.answer(file=output)
