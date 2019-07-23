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


from pyrogram import Client, Filters, MessageHandler

from userbot import client


IMPORTED = []

on_message = Client.on_message


def outgoing(
    pattern : str,
    prefix : (str, None) = "^[!.#]",
    cs : bool = False
) -> callable:

    regex = prefix + pattern if prefix else pattern
    regexp = '(?i)' + regex if not cs else regex

    return Client.on_message(
        Filters.outgoing & Filters.regex(regexp)
    )


def message_handler(filters=None, group : int = 0) -> callable:

    def decorator(callback: callable) -> callable:
        handler = client.add_handler(
            MessageHandler(callback, filters), group
        )
        IMPORTED.append(handler)

        return handler

    return decorator


def main_handler(command: str) -> callable:

    def decorator(callback: callable) -> callable:
        filters = (
            Filters.outgoing & \
            ~Filters.edited & \
            Filters.regex(f"^[!.]{command}$")
        )
        handler = client.add_handler(
            MessageHandler(callback, filters), 0
        )
        IMPORTED.append(handler)

        return handler

    return decorator