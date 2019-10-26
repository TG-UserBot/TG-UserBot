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


import redis
import userbot.utils.client

from configparser import ConfigParser
from os.path import abspath, basename, dirname, isfile, join
from packaging.version import parse
from sys import exit, platform, version_info
from logging import (
    getLogger, DEBUG, INFO, ERROR, CRITICAL
)

from telethon.tl.types import User
from userbot.utils.sessions import RedisSession
from userbot.utils.helpers import resolve_env

UserBotClient = userbot.utils.client.UserBotClient
config = ConfigParser()

config_file = join(dirname(dirname(__file__)), 'config.ini')
pyversion = ".".join(str(num) for num in version_info if isinstance(num, int))

if parse(pyversion) < parse('3.7'):
    print(
        "Please run this script with Python 3.7 or above."
        "\nExiting the script."
    )
    exit(1)

if basename(abspath('.')) == 'source':  # To avoid errors from Sphinx
    sphinx = True
else:
    sphinx = False

if isfile(config_file) or sphinx:
    if sphinx:
        config_file = join(dirname(dirname(__file__)), 'sample_config.ini')
    config.read(config_file)
else:
    try:
        resolve_env(config)
    except ValueError:
        print(
            "Please make sure you have a proper config.ini in this directory "
            "or the required environment variables set."
            "\nExiting the script."
        )
        exit(1)

ROOT_LOGGER = getLogger()
LOGGER = getLogger(__name__)

userbot = config['userbot']
telethon = config['telethon']

LOGGER_CHAT_ID = userbot.getint('logger_group_id', 0)
CONSOLE_LOGGER = userbot.get('console_logger_level', 'INFO')
REDIS_ENDPOINT = telethon.get('redis_endpoint', None)
REDIS_PASSWORD = telethon.get('redis_password', None)

if not REDIS_ENDPOINT or not REDIS_PASSWORD:
    LOGGER.info(
        "Consider making an account on redislab.com and updating your config "
        "with the redis endpoint and password, if you want to run on Heroku!"
    )
    redis_session = False
    session = "userbot"
else:
    REDIS_HOST = REDIS_ENDPOINT.split(':')[0]
    REDIS_PORT = REDIS_ENDPOINT.split(':')[1]
    redis_connection = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD
    )
    try:
        redis_connection.ping()
    except Exception as e:
        LOGGER.exception(e)
        print()
        LOGGER.warning(
            "Make sure you have the correct Redis endpoint and password."
        )
        exit(1)
    redis_session = True
    session = RedisSession("userbot", redis_connection)

LEVELS = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'ERROR': ERROR,
    'CRITICAL': CRITICAL
}


if CONSOLE_LOGGER.upper() in LEVELS:
    level = LEVELS[CONSOLE_LOGGER.upper()]
    ROOT_LOGGER.setLevel(level)
    LOGGER.setLevel(level)


if platform.startswith('win'):
    from asyncio import ProactorEventLoop
    from os import system

    loop = ProactorEventLoop()
    system('color')
else:
    loop = None

__version__ = "0.4"
__license__ = "GNU General Public License v3.0"
__author__ = 'Kandarp <https://github.com/kandnub>'
__copyright__ = (
    "TG-UserBot  Copyright (C) 2019  Kandarp <https://github.com/kandnub>"
)

client = UserBotClient(
    session=session,
    api_id=telethon.getint('api_id', None),
    api_hash=telethon.get('api_hash', None),
    loop=loop,
    app_version=__version__
)

client.version = __version__
client.config = config
client.prefix = userbot.get('prefix', None)


def verifyLoggerGroup(client: UserBotClient) -> None:
    client.logger = True

    def disable_logger(error: str):
        if LOGGER_CHAT_ID != 0:
            LOGGER.error(error)
        client.logger = False

    try:
        entity = client.loop.run_until_complete(
            client.get_entity(LOGGER_CHAT_ID)
        )
        if not isinstance(entity, User):
            if not entity.creator:
                if entity.default_banned_rights.send_messages:
                    disable_logger(
                        "Permissions missing to send messages "
                        "for the specified Logger group."
                    )
    except ValueError:
        disable_logger(
            "Logger group ID cannot be found. "
            "Make sure it's correct."
        )
    except TypeError:
        disable_logger(
            "Logger group ID is unsupported. "
            "Make sure it's correct."
        )
    except Exception as e:
        disable_logger(
            "An Exception occured upon trying to verify "
            "the logger group.\n" + str(e)
        )
