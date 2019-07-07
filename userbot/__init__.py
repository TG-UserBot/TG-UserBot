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


from configparser import ConfigParser
from os.path import isfile
from sys import exit, platform, version_info
from logging import (basicConfig, getLogger, NOTSET, DEBUG,
    INFO, WARNING, ERROR, CRITICAL)

from pyrogram import Client


if not version_info >= (3, 7, 3):
    print("Please run this script with Python 3.7.3 or above.")
    exit(1)
elif not isfile('config.ini'):
    print("Please make sure you have a proper config.ini in this directory.\nExiting.")
    exit(1)


LOG = getLogger(__name__)

configparser = ConfigParser()
configparser.read('config.ini')
LOGGER_CHAT_ID = configparser['userbot'].getint('LOGGER_CHAT_ID', 0)
CONSOLE_LOGGER = configparser['userbot'].get('CONSOLE_LOGGER', 'WARNING')
USERBOT_LOGGER = True if LOGGER_CHAT_ID else False

CONSOLE_LOGGER_FORMAT = "[%(levelname)s / %(asctime)s] %(name)s: %(message)s"

LEVELS = {'NOTSET': NOTSET, 'DEBUG': DEBUG, 'INFO': INFO,\
          'WARNING': WARNING, 'ERROR': ERROR, 'CRITICAL': CRITICAL}


if CONSOLE_LOGGER.upper() in LEVELS:
    level = LEVELS[CONSOLE_LOGGER.upper()]
    basicConfig(format=CONSOLE_LOGGER_FORMAT, datefmt="%x - %X %p", level=level)
else:
    basicConfig(format=CONSOLE_LOGGER_FORMAT, datefmt="%x - %X %p" , level=WARNING)

if platform.startswith('win'):
    from asyncio import ProactorEventLoop, set_event_loop
    set_event_loop(ProactorEventLoop())


__version__ =  "0.2"
__license__ = "GNU General Public License v3.0"
__copyright__ = "TG-UserBot  Copyright (C) 2019  Kandarp <https://github.com/kandnub>"

client = Client("userbot", app_version=__version__)