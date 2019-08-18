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


from logging import Formatter, DEBUG, INFO, WARNING, ERROR, CRITICAL


CCRI = '\033[48;5;124m'
CERR = '\033[38;5;124m'
CWAR = '\033[38;5;202m'
CINF = '\033[38;5;15m'
CDEB = '\033[38;5;28m'
CEND = '\033[0m'
CPYR = '\033[33;1m'
CBOT = '\033[94'
CUSR = '\033[38;5;118m'


class CustomFormatter(Formatter):
    """Convert a :obj:`LogRecord<logging.LogRecord>` to a string.

    Uses ANSI escape codes to colour some specific strings.
    """

    def format(self, record) -> str:
        """Format the record dictionary to a readable string.

        Args:
            record (``dict``):
                The attribute dictionary.

        Returns:
            ``str``:
                Formatted string for userbot and pyrogram logs.
        """
        first_half = "[%(asctime)s / %(levelname)s]"

        if record.name.startswith('userbot'):
            second_half = (
                " {0};1m%(name)s:{1} %(message)s".format(CBOT, CEND)
            )
        elif record.name.startswith('pyrogram'):
            second_half = (
                " {0}%(name)s:{1} %(message)s".format(CPYR, CEND)
            )
        else:
            second_half = " %(name)s: %(message)s"

        FORMATS = {
            CRITICAL: CCRI + first_half + CEND + second_half,
            ERROR: CERR + first_half + CEND + second_half,
            WARNING: CWAR + first_half + CEND + second_half,
            INFO: CINF + first_half + CEND + second_half,
            DEBUG: CDEB + first_half + CEND + second_half,
            'DEFAULT': first_half + second_half
        }

        log_fmt = FORMATS.get(record.levelno, FORMATS['DEFAULT'])
        formatter = Formatter(fmt=log_fmt, datefmt='%X', style='%')

        return formatter.format(record)
