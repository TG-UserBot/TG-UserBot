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


from os import remove

from . import client


async def limit_exceeded(
    event,
    message,
    reply : bool = False
):
    with open("output.txt", "w+") as f:
        f.write(message.strip())
    if reply:
        sent = await event.reply_document(
            document="output.txt"
        )
    else:
        sent = await client.send_document(
            event.chat.id,
            document="output.txt"
        )
    remove("output.txt")
    return sent