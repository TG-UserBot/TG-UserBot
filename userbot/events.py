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


commands_dict = {}
main_handlers = []
on_message = Client.on_message


def bot_commands() -> dict:
    """A dict of all the commands handlers.

    Returns:
        ``dict``
    """
    return commands_dict


def clear_commands_dict():
    """Clears the old bot commands ``dict``."""
    return commands_dict.clear()


def commands(command: str) -> callable:
    """Add a function's handler to it's command name.

    Args:
        command (``str``):
            The command name to use.
    """

    def wrapper(func) -> callable:
        commands_dict.update({command: func.handler})
        return func

    return wrapper


def basic_command(
    command: str,
    prefix: str = "[!.#]",
    group: int = 0
) -> callable:
    """Create simple commands by just providing the pattern without the prefix.

    Args:
        command (``str``):
            The pattern you want to use, excluding the prefix.
        prefix (``str``, optional):
            If you want to change the default prefix set.
            Defaults to "[!.#]".
        group (``int``, optional):
            The group to use for the message handler. Defaults to 0.
    """

    filters = (
        Filters.outgoing &
        Filters.regex(f"(?i)^{prefix}{command}")
    )

    return Client.on_message(filters, group)


def main_command(command: str) -> callable:
    """Add a strict pattern with the prefix and suffix set for
    the commands in __main__.py.

    Args:
        command (``str``):
            The command to set.
    """

    def decorator(callback: callable) -> callable:
        filters = (
            Filters.outgoing & ~Filters.edited &
            Filters.regex(f"^[!.]{command}$")
        )
        handler = client.add_handler(
            MessageHandler(callback, filters), 0
        )
        main_handlers.append(handler)

        return callback

    return decorator
