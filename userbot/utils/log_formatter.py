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


import logging
import os


HEROKU = os.environ.get('DYNO', False)
CCRI = '\033[48;5;124m' if not HEROKU else ''
CERR = '\033[38;5;124m' if not HEROKU else ''
CWAR = '\033[38;5;202m' if not HEROKU else ''
CINF = '\033[38;5;15m' if not HEROKU else ''
CDEB = '\033[38;5;28m' if not HEROKU else ''
CEND = '\033[0m' if not HEROKU else ''
CORA = '\033[33;1m' if not HEROKU else ''
CBOT = '\033[94;1m' if not HEROKU else ''
CUSR = '\033[38;5;118m' if not HEROKU else ''


class CustomPercentStyle(logging.PercentStyle):
    """Replace the default_format to our own and override the format method."""
    default_format = "[%(levelname)s / %(asctime)s] %(name)s: %(message)s"

    def format(self, record):
        """Use ANSI escape code for the default format, else ignore it"""
        super().format(record)
        if self._fmt == self.default_format:
            if HEROKU:
                first = "[%s] " % (record.levelname[:1])
            else:
                first = "[%(asctime)s / %(levelname)s] "

            if record.name.startswith('telethon'):
                second = f"{CBOT}%(name)s:{CEND} %(message)s"
            elif record.name.startswith('userbot'):
                second = f"{CORA}%(name)s:{CEND} %(message)s"
            else:
                second = "%(name)s: %(message)s"

            FORMATS = {
                logging.CRITICAL: CCRI + first + CEND + second,
                logging.ERROR: CERR + first + CEND + second,
                logging.WARNING: CWAR + first + CEND + second,
                logging.INFO: CINF + first + CEND + second,
                logging.DEBUG: CDEB + first + CEND + second,
                'DEFAULT': self.default_format
            }
            fmt = FORMATS.get(record.levelno, FORMATS['DEFAULT'])
        else:
            fmt = self._fmt
        return fmt % record.__dict__


class CustomFormatter(logging.Formatter):
    """Update the default Formatter's _STYLES dict to use our custom one"""
    _STYLES = logging._STYLES.update({
        '%': (CustomPercentStyle, logging.BASIC_FORMAT)
    })
