# TG-UserBot - A modular Telegram UserBot for Python3.6+. 
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


from os import environ, path
from sys import exit, platform, version_info
from re import split
from dotenv import load_dotenv
from json import loads
from logging import basicConfig, getLogger, NOTSET, DEBUG,\
                    INFO, WARNING, ERROR, CRITICAL

from telethon import TelegramClient


load_dotenv('./config.env')

LOG = getLogger(__name__)

API_HASH = environ.get("API_HASH", None)

API_KEY = int(environ.get("API_KEY")) if environ.get("API_KEY").isdigit() else None

BOT_TOKEN = environ.get("BOT_TOKEN", None)

CONSOLE_LOGGER = environ.get("CONSOLE_LOGGER", "INFO")

DONT_LOAD_MODULES = split(r"\W+", environ.get("DONT_LOAD", "[]"))

DONT_LOAD = [module for module in DONT_LOAD_MODULES if module]

USERBOT_LOGGER_GROUP = int(environ.get("USERBOT_LOGGER_GROUP", 0))

USERBOT_LOGGER = True if USERBOT_LOGGER_GROUP else False


if platform.startswith('win'):
    from asyncio import ProactorEventLoop
    loop = ProactorEventLoop()
else:
    loop = None

python_version = (version_info[0], version_info[1], version_info[2])

CONSOLE_LOGGER_FORMAT = "[%(levelname)s / %(asctime)s] %(name)s: %(message)s"

LEVELS = {'NOTSET': NOTSET, 'DEBUG': DEBUG, 'WARNING': WARNING,\
          'ERROR': ERROR, 'CRITICAL': CRITICAL}


if python_version < (3, 6):
    LOG.error("At least Python 3.6 is required to run.")
    exit(1)
elif not path.isfile('userbot.session'):
    LOG.error("Please generate a session with generate_session.py first.")
    exit(1)
elif not API_KEY or not API_HASH:
    LOG.error("Please make sure you have your API ID and HASH set in config or env vars.")
    exit(1)

if CONSOLE_LOGGER.upper() in LEVELS:
    level = LEVELS[CONSOLE_LOGGER.upper()]
    basicConfig(format=CONSOLE_LOGGER_FORMAT, level=level)
else:
    basicConfig(format=CONSOLE_LOGGER_FORMAT, level=INFO)


__version__ =  "0.1"
__license__ = "GNU General Public License v3.0"
__copyright__ = "TG-UserBot  Copyright (C) 2019  Kandarp <https://github.com/kandnub>"

client = TelegramClient("userbot", API_KEY, API_HASH, app_version=__version__, loop=loop)