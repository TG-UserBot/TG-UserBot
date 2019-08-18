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
from typing import Union

from .. import client
from pyrogram import Message


async def limit_exceeded(
    event: Message,
    message: str,
    reply: bool = False
) -> Union[Message, None]:
    """Send text as a .txt file if it's length exceeds TG limit.

    Args:
        event (:obj:`Message<pyrogram.Message>`):
            Pyrogram's Message object.
        message (``str``):
            The text string to send.
        reply (``bool``, optional):
            If you want the send the document as a reply. Defaults to False.

    Returns:
        :obj:`Message<pyrogram.Message>` | ``None``:
            Sent document's Message object if successfull, None otherwise.

    Raises:
        `RPCError`:
            In case of a Telegram RPC error.
    """
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
