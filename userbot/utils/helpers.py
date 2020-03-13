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
import configparser
import datetime
import logging
import os
import os.path
import sys
from typing import Union

from heroku3 import from_key

from telethon import errors
from telethon.tl import types
from telethon.utils import get_display_name

from .client import UserBotClient
from .log_formatter import CEND, CUSR
from .events import NewMessage
from userbot.plugins import plugins_data


LOGGER = logging.getLogger(__name__)
sample_config_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'sample_config.ini'
)


def printUser(entity: types.User) -> None:
    """Print the user's first name + last name upon start"""
    user = get_display_name(entity)
    print(
        "\nSuccessfully logged in as {0}{2}{1}".format(CUSR, CEND, user)
    )


def printVersion(version: int, prefix: str) -> None:
    """Print the version of the bot with the default prefix"""
    if not prefix:
        prefix = '.'
    print(
        "{0}UserBot v{2}{1} is running, test it by sending {3}ping in"
        " any chat.\n".format(CUSR, CEND, version, prefix)
    )


def resolve_env(config: configparser.ConfigParser):
    """Check the environment variables and add them a configparser obj"""
    api_id = os.getenv('api_id', None)
    api_hash = os.getenv('api_hash', None)
    redis_endpoint = os.getenv('redis_endpoint', None)
    redis_password = os.getenv('redis_password', None)

    if "telethon" in config.sections() and not api_id and not api_hash:
        api_id = config['telethon'].get('api_id', False)
        api_hash = config['telethon'].get('api_hash', False)

    if not api_id or not api_hash:
        raise ValueError('You need to set your API Keys at least.')

    sample_config = configparser.ConfigParser()
    sample_config.read(sample_config_file)
    for section in sample_config.sections():
        if section not in config:
            config[section] = {}

    config['telethon']['api_id'] = api_id
    config['telethon']['api_hash'] = api_hash
    if redis_endpoint:
        config['telethon']['redis_endpoint'] = redis_endpoint
    if redis_password:
        config['telethon']['redis_password'] = redis_password

    userbot = {
        'pm_permit': bool(os.getenv('pm_permit', None)),
        'console_logger_level': os.getenv('console_logger_level', None),
        'logger_group_id': os.getenv('logger_group_id', None),
        'userbot_prefix': os.getenv('userbot_prefix', None),
        'default_sticker_pack': os.getenv('default_sticker_pack', None),
        'default_animated_sticker_pack': os.getenv(
            'default_animated_sticker_pack', None
        )
    }

    api_keys = {
        'api_key_heroku': os.getenv(
            'api_key_heroku', None
        ),
        'api_key_removebg': os.getenv(
            'api_key_removebg', None
        )
    }

    make_config(config, 'userbot', userbot)
    make_config(config, 'api_keys', api_keys)


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


def make_config(
    config: configparser.ConfigParser,
    section: str, section_dict: dict
) -> None:
    UNACCETPABLE = ['', '0', 'None', 'none', 0, None]
    for key, value in section_dict.items():
        if value is not None and value not in UNACCETPABLE:
            config[section][key] = str(value)


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
        text = "\u221E (less than 1 second)"
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
