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


class CustomFormatter(logging.Formatter):
    """Convert a :obj:`LogRecord<logging.LogRecord>` to a string.

    Uses ANSI escape codes to colour some specific strings.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format the record dictionary to a readable string.

        Args:
            record (:obj:`LogRecord<logging.LogRecord>`):
                The attribute dictionary.

        Returns:
            ``str``:
                Formatted string for userbot and pyrogram logs.
        """
        super().format(record)
        record.message = record.getMessage()
        time = self.formatTime(record, "%X")
        if HEROKU:
            first = "[%s] " % (record.levelname[:1])
        else:
            first = "[%s / %s] " % (time, record.levelname)

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
            'DEFAULT': first + second
        }

        log_fmt = FORMATS.get(record.levelno, FORMATS['DEFAULT'])
        return log_fmt % record.__dict__
