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
from importlib import invalidate_caches, reload
from logging import StreamHandler
from sys import exit, modules

from userbot import (client, __copyright__, __license__, __version__,
    LOGGER, ROOT_LOGGER)
from userbot.events import IMPORTED, main_handler
from userbot.helper_funcs.logFormatter import CustomFormatter, CUSR, CEND


handler = StreamHandler()
handler.setFormatter(CustomFormatter())

ROOT_LOGGER.addHandler(handler)

loop = get_event_loop()

async def restarter(c, event):
    invalidate_caches()
    plugins = c.plugins['root'].replace("/", ".")
    helper_funcs = 'userbot.helper_funcs'
    events = 'userbot.events'
    for module in modules:
        if module.startswith((plugins, helper_funcs, events)):
            try:
                reload(modules[module])
            except Exception as e:
                LOGGER.warning(f"\nFailed to reload {module}. Ignoring.")
                print(e)
                print("\n")

    await c.restart()

    for handlerObj in IMPORTED:
        handler, group = handlerObj
        client.add_handler(handler, group)

    LOGGER.warning("Successfully restarted the Pyrogram client.")
    LOGGER.warning(f"Successfully reloaded {len(IMPORTED)} main functions.")
    await event.edit("`Successfully restarted the Pyrogram client.`")


@main_handler(command="restart")
async def restart(c, event):
    loop.create_task(restarter(c, event))

@main_handler(command="shutdown")
async def shutdown(c, event):
    await event.edit(
        "`Stopping the Pyrogram client and exiting the script.`"
    )
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

    LOGGER.warning(f"Successfully loaded {len(IMPORTED)} main functions.")
    print(__copyright__)
    print("Licensed under the terms of the " + __license__)
    print(
        "You're currently logged in as {0}{2}.{1}"\
        .format(CUSR, CEND, user)
    )
    print(
        "{0}UserBot v{2}{1} is running, test it by sending .ping in"
        " any chat.\n".format(CUSR, CEND, __version__)
    )

    await client.idle()


if __name__ ==  '__main__':
    loop.run_until_complete(main())