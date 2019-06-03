from os import environ, path
from sys import exit, version_info
from re import split
from dotenv import load_dotenv
from json import loads
from logging import basicConfig, getLogger, NOTSET, DEBUG,\
                    INFO, WARNING, ERROR, CRITICAL

from telethon import TelegramClient


python_version = (version_info[0], version_info[1], version_info[2])
load_dotenv('./config.env')

API_KEY = int(environ.get("API_KEY")) if environ.get("API_KEY").isdigit() else None
API_HASH = environ.get("API_HASH", None)
USERBOT_LOGGER_GROUP = int(environ.get("USERBOT_LOGGER_GROUP", 0))
USERBOT_LOGGER = USERBOT_LOGGER_GROUP if USERBOT_LOGGER_GROUP else None
DONT_LOAD_MODULES = split(r"\W+", environ.get("DONT_LOAD", None))
DONT_LOAD = [module for module in DONT_LOAD_MODULES if module] 
BOT_TOKEN = environ.get("BOT_TOKEN", None)

CONSOLE_LOGGER = environ.get("CONSOLE_LOGGER", "INFO")
CONSOLE_LOGGER_FORMAT = "[%(levelname)s / %(asctime)s] %(name)s: %(message)s"
LEVELS = {'NOTSET': NOTSET, 'DEBUG': DEBUG, 'WARNING': WARNING,\
          'ERROR': ERROR, 'CRITICAL': CRITICAL}

if CONSOLE_LOGGER.upper() in LEVELS:
    level = LEVELS[CONSOLE_LOGGER.upper()]
    basicConfig(format=CONSOLE_LOGGER_FORMAT, level=level)
else:
    basicConfig(format=CONSOLE_LOGGER_FORMAT, level=INFO)
LOG = getLogger(__name__)

if python_version < (3, 6):
    LOG.error("At least Python 3.6 is required to run.")
    exit(1)
elif not path.isfile('userbot.session'):
    LOG.error("Please generate a session with generate_session.py first.")
    exit(1)
elif not API_KEY or not API_HASH:
    LOG.error("Please make sure you have your API ID and HASH set in config or env vars.")
    exit(1)


client = TelegramClient("userbot", API_KEY, API_HASH)

__version__ =  "0.1"
__license__ = "GNU General Public License v3.0"
__copyright__ = "TG-UserBot  Copyright (C) 2019  Kandarp <https://github.com/kandnub>"