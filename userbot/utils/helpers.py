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


import os

from telethon.tl.types import User
from telethon.utils import get_display_name

import userbot.helper_funcs.log_formatter as log_formatter


CUSR = log_formatter.CUSR
CEND = log_formatter.CEND


def printUser(entity: User) -> None:
    user = get_display_name(entity)
    print(
        "\nSuccessfully logged in as {0}{2}{1}".format(CUSR, CEND, user)
    )


def printVersion(version: int, prefix: str) -> None:
    if not prefix:
        prefix = '.'
    print(
        "{0}UserBot v{2}{1} is running, test it by sending {3}ping in"
        " any chat.\n".format(CUSR, CEND, version, prefix)
    )


def resolve_env(config):

    api_id = os.getenv('api_id', None)
    api_hash = os.getenv('api_hash', None)
    redis_endpoint = os.getenv('redis_endpoint', None)
    redis_password = os.getenv('redis_password', None)

    if not api_id or not api_hash:
        raise ValueError

    config['telethon'] = {}
    config['telethon']['api_id'] = api_id
    config['telethon']['api_hash'] = api_hash
    if redis_endpoint:
        config['telethon']['redis_endpoint'] = redis_endpoint
    if redis_password:
        config['telethon']['redis_password'] = redis_password

    userbot = {
        'console_logger_level': os.getenv('console_logger_level', None),
        'logger_group_id': int(os.getenv('logger_group_id', 0)),
        'prefix': os.getenv('prefix', None),
        'default_sticker_pack': os.getenv('default_sticker_pack', None),
        'default_animated_sticker_pack': os.getenv(
            'default_animated_sticker_pack', None
        )
    }

    config['userbot'] = {}
    for key, value in userbot.items():
        if value is not None and value != 0:
            config['userbot'][key] = str(value)
