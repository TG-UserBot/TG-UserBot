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


import asyncio
import datetime
import logging
import os
import os.path
import sys
import time
from typing import Tuple, Union

from heroku3 import from_key

from telethon import errors
from telethon.tl import types
from telethon.utils import get_display_name

from .client import UserBotClient
from .log_formatter import CEND, CUSR
from .events import NewMessage
from userbot.plugins import plugins_data


LOGGER = logging.getLogger('userbot')


def printUser(entity: types.User) -> None:
    """Print the user's first name + last name upon start"""
    user = get_display_name(entity)
    print()
    LOGGER.warning(
        "Successfully logged in as {0}{2}{1}".format(CUSR, CEND, user)
    )


def printVersion(version: int, prefix: str) -> None:
    """Print the version of the bot with the default prefix"""
    if not prefix:
        prefix = '.'
    LOGGER.warning(
        "{0}UserBot v{2}{1} is running, test it by sending {3}ping in"
        " any chat.".format(CUSR, CEND, version, prefix)
    )
    print()


async def isRestart(client: UserBotClient) -> None:
    """Check if the script restarted itself and edit the last message"""
    userbot_restarted = os.environ.get('userbot_restarted', False)
    heroku = client.config['api_keys'].get('api_key_heroku', False)
    updated = os.environ.pop('userbot_update', False)
    disabled_commands = False

    async def success_edit(text):
        entity = int(userbot_restarted.split('/')[0])
        message = int(userbot_restarted.split('/')[1])
        try:
            await client.edit_message(entity, message, text)
        except (
            ValueError, errors.MessageAuthorRequiredError,
            errors.MessageNotModifiedError, errors.MessageIdInvalidError
        ):
            LOGGER.debug(f"Failed to edit message ({message}) in {entity}.")
            pass

    if updated:
        text = "`Successfully updated and restarted the userbot!`"
    else:
        text = '`Successfully restarted the userbot!`'
    if userbot_restarted:
        del os.environ['userbot_restarted']
        LOGGER.debug('Userbot was restarted! Editing the message.')
        if os.environ.get('DYNO', False) and heroku:
            heroku_conn = from_key(heroku)
            HEROKU_APP = os.environ.get('HEROKU_APP_NAME', False)
            if HEROKU_APP:
                app = heroku_conn.apps()[HEROKU_APP]
                for build in app.builds():
                    if build.status == "pending":
                        return
                if app.config()['userbot_update']:
                    del app.config()['userbot_update']
                    await success_edit(
                        "`Successfully deployed a new image to heroku "
                        "and restarted the userbot.`"
                    )
                else:
                    await success_edit(text)
                del app.config()['userbot_restarted']
                disabled_commands = app.config()['userbot_disabled_commands']
                del app.config()['userbot_disabled_commands']
        else:
            await success_edit(text)
            disabled_commands = os.environ.get(
                'userbot_disabled_commands', False
            )

        if "userbot_disabled_commands" in os.environ:
            del os.environ['userbot_disabled_commands']
        if disabled_commands:
            await disable_commands(client, disabled_commands)


def restarter(client: UserBotClient) -> None:
    args = [sys.executable, "-m", "userbot"]
    if client.disabled_commands:
        disabled_list = ", ".join(client.disabled_commands.keys())
        os.environ['userbot_disabled_commands'] = disabled_list
    if os.environ.get('userbot_afk', False):
        plugins_data.dump_AFK()
    client._kill_running_processes()

    if sys.platform.startswith('win'):
        os.spawnle(os.P_NOWAIT, sys.executable, *args, os.environ)
    else:
        os.execle(sys.executable, *args, os.environ)


async def restart(event: NewMessage.Event) -> None:
    event.client.reconnect = False
    restart_message = f"{event.chat_id}/{event.message.id}"
    os.environ['userbot_restarted'] = restart_message
    restarter(event.client)
    if event.client.is_connected():
        await event.client.disconnect()


async def _humanfriendly_seconds(seconds: int or float) -> str:
    elapsed = datetime.timedelta(seconds=round(seconds)).__str__()
    splat = elapsed.split(', ')
    if len(splat) == 1:
        return await _human_friendly_timedelta(splat[0])
    friendly_units = await _human_friendly_timedelta(splat[1])
    return ', '.join([splat[0], friendly_units])


async def _human_friendly_timedelta(timedelta: str) -> str:
    splat = timedelta.split(':')
    nulls = ['0', "00"]
    h = splat[0]
    m = splat[1]
    s = splat[2]
    text = ''
    if h not in nulls:
        unit = "hour" if h == 1 else "hours"
        text += f"{h} {unit}"
    if m not in nulls:
        unit = "minute" if m == 1 else "minutes"
        delimiter = ", " if len(text) > 1 else ''
        text += f"{delimiter}{m} {unit}"
    if s not in nulls:
        unit = "second" if s == 1 else "seconds"
        delimiter = " and " if len(text) > 1 else ''
        text += f"{delimiter}{s} {unit}"
    if len(text) == 0:
        text = "\u221E"
    return text


async def get_chat_link(
    arg: Union[types.User, types.Chat, types.Channel, NewMessage.Event],
    reply=None
) -> str:
    if isinstance(arg, (types.User, types.Chat, types.Channel)):
        entity = arg
    else:
        entity = await arg.get_chat()

    if isinstance(entity, types.User):
        if entity.is_self:
            name = "yourself"
        else:
            name = get_display_name(entity) or "Deleted Account?"
        extra = f"[{name}](tg://user?id={entity.id})"
    else:
        if hasattr(entity, 'username') and entity.username is not None:
            username = '@' + entity.username
        else:
            username = entity.id
        if reply is not None:
            if isinstance(username, str) and username.startswith('@'):
                username = username[1:]
            else:
                username = f"c/{username}"
            extra = f"[{entity.title}](https://t.me/{username}/{reply})"
        else:
            if isinstance(username, int):
                username = f"`{username}`"
                extra = f"{entity.title} ( {username} )"
            else:
                extra = f"[{entity.title}](tg://resolve?domain={username})"
    return extra


async def disable_commands(client: UserBotClient, commands: str) -> None:
    commands = commands.split(", ")
    for command in commands:
        target = client.commands.get(command, False)
        if target:
            client.remove_event_handler(target.func)
            client.disabled_commands.update({command: target})
            del client.commands[command]
            LOGGER.debug("Disabled command: %s", command)


async def is_ffmpeg_there():
    cmd = await asyncio.create_subprocess_shell(
        'ffmpeg -version',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await cmd.communicate()
    return True if cmd.returncode == 0 else False


async def format_speed(speed_per_second, unit):
    unit0 = unit[0].lower()
    base, unit0 = (1024, "Byte") if unit[0] == 'byte' else (1000, "bit")
    seq = ['', 'K', 'M', 'G']
    speed = speed_per_second / unit[1]
    for i in seq:
        if speed/base < 1:
            return speed, i, unit0
        speed /= base


async def calc_eta(elp: float, speed: int, current: int, total: int) -> int:
    if total is None or total == 0:
        return 0
    if current == 0 or elp < 0.001:
        return 0
    speed = speed if speed else 1
    return int((float(total) - float(current)) / speed)


def ul_progress(d: dict, event) -> Tuple[Union[str, bool], bool]:
    """ Logs the upload progress """
    now = datetime.datetime.now(datetime.timezone.utc)
    log_text = (
        "Uploaded %(current)s of %(total)s. "
        "Progress: %(percentage)s%% speed: %(speed)s"
        "Time elapsed: %(elp)s"
    )
    LOGGER.debug(log_text % d)
    text = (
        "`Uploading %(filen)s at %(speed)s.`\n"
        "__Progress: %(percentage)s%% of %(total)s__\n"
        "__ETA: %(eta)s, Elapsed: %(elp)s__"
    )

    if d.get('percentage', 0) == 100:
        return "__Successfully uploaded %(filen)s in %(elp)s!__" % d, True
    elif (now - event.date).total_seconds() > 5:
        return text % d, False
    return False, False


def dl_progress(d: dict, event) -> Tuple[Union[str, bool], bool]:
    """ Logs the download progress """
    now = datetime.datetime.now(datetime.timezone.utc)
    log_text = (
        "Downloaded %(current)s of %(total)s. "
        "Progress: %(percentage)s%%"
        "Time elapsed: %(elp)s"
    )
    LOGGER.debug(log_text % d)
    text = (
        "`Downloading %(filen)s at %(speed)s.`\n"
        "__Progress: %(percentage)s%% of %(total)s__\n"
        "__ETA: %(eta)s, Elapsed: %(elp)s__"
    )

    if d.get('percentage', 0) == 100:
        return "__Successfully downloaded %(filen)s in %(elp)s!__" % d, True
    elif (now - event.date).total_seconds() > 5:
        return text % d, False
    return False, False


class ProgressCallback():
    """Custom class to handle upload and download progress."""
    def __init__(self, event, start=None, filen='unamed'):
        self.event = event
        self.start = start or time.time()
        self.last_edit = None
        self.filen = filen
        self.upload_finished = False
        self.download_finished = False

    async def resolve_prog(self, current, total):
        """Calculate the necessary info and make a dict from it."""
        if not self.last_edit:
            self.last_edit = datetime.datetime.now(datetime.timezone.utc)
        now = time.time()
        elp = now - self.start
        speed = int(float(current) / elp)
        eta = await calc_eta(elp, speed, current, total)
        s0, s1, s2 = await format_speed(speed, ("byte", 1))
        c0, c1, c2 = await format_speed(current, ("byte", 1))
        t0, t1, t2 = await format_speed(total, ("byte", 1))
        percentage = round(current / total * 100, 2)
        return {
            'filen': self.filen, 'percentage': percentage,
            'eta': await _humanfriendly_seconds(eta),
            'elp': await _humanfriendly_seconds(elp),
            'current': f'{c0:.2f}{c1}{c2[0]}',
            'total': f'{t0:.2f}{t1}{t2[0]}',
            'speed': f'{s0:.2f}{s1}{s2[0]}/s'
        }

    async def up_progress(self, current, total):
        """Handle the upload progress only."""
        d = await self.resolve_prog(current, total)
        edit, finished = ul_progress(d, self.event)
        if finished:
            if not self.upload_finished:
                self.event = await self.event.answer(edit)
                self.upload_finished = True
        elif edit:
            self.event = await self.event.answer(edit)

    async def dl_progress(self, current, total):
        """Handle the download progress only."""
        d = await self.resolve_prog(current, total)
        edit, finished = dl_progress(d, self.event)
        if finished:
            if not self.download_finished:
                self.event = await self.event.answer(edit)
                self.download_finished = True
        elif edit:
            self.event = await self.event.answer(edit)
