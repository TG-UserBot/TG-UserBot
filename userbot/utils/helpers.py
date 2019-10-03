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


from telethon.tl.types import User
from telethon.utils import get_display_name

from userbot.helper_funcs.log_formatter import CUSR, CEND


def printUser(entity: User) -> None:
    user = get_display_name(entity)
    print(
        "\nSuccessfully logged in as {0}{2}{1}".format(CUSR, CEND, user)
    )


def printVersion(version: int, prefix: str) -> None:
    print(
        "{0}UserBot v{2}{1} is running, test it by sending {3}ping in"
        " any chat.\n".format(CUSR, CEND, version, prefix)
    )
