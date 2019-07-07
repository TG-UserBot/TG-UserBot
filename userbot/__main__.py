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


from asyncio import get_event_loop
from sys import exit
from pyrogram import Filters

from userbot import client, __copyright__, __license__, LOG, __version__
from userbot.events import IMPORTED, message_handler


loop = get_event_loop()

async def restarter(c, event):
    await c.restart()

    for handlerObj in IMPORTED:
        handler, group = handlerObj
        client.add_handler(handler, group)

    LOG.warning(f"Pyrogram client restarted.")
    LOG.warning(f"Successfully reloaded {len(IMPORTED)} main functions.")
    await event.edit("`Successfully restarted the Pyrogram client.`")


@message_handler(Filters.outgoing & Filters.regex("^[!.#]restart$"), 0)
async def restart(c, event):
    loop.create_task(restarter(c, event))

@message_handler(Filters.outgoing & Filters.regex("^[!.#]shutdown$"), 0)
async def shutdown(c, event):
    await event.edit("`Stopping the Pyrogram client and exiting the script.`")
    loop.create_task(client.stop())
    print("\nUserBot script exiting.")
    exit()


async def main():
    await client.start()

    me = await client.get_me()
    if me.username:
        user = me.username
    else:
        user = me.first_name + " [" + me.id + "]"

    LOG.warning(f"Successfully loaded {len(IMPORTED)} main functions.")
    print(__copyright__)
    print("Licensed under the terms of the " + __license__)
    print(f"You're currently logged in as {user}.")
    print(f"UserBot v{__version__} is running, test it by sending .ping in any chat.\n")

    await client.idle()


if __name__ ==  '__main__':
    loop.run_until_complete(main())