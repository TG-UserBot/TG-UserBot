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


from asyncio import get_event_loop
from importlib import invalidate_caches, reload
from logging import StreamHandler
from sys import exit, modules

from userbot import (
    client, __copyright__, __license__, __version__, LOGGER, ROOT_LOGGER
)
from userbot.events import (
    bot_commands, clear_commands_dict, main_command, main_handlers
)
from userbot.helper_funcs.log_formatter import CustomFormatter, CUSR, CEND


handler = StreamHandler()
handler.setFormatter(CustomFormatter())

ROOT_LOGGER.addHandler(handler)

loop = get_event_loop()
disabled_commands = {}


async def restarter(c, event):
    def_text = "`Successfully restarted the Pyrogram client.`"

    clear_commands_dict()
    disabled_commands.clear()
    invalidate_caches()
    plugins = c.plugins['root'].replace("/", ".")
    helper_funcs = 'userbot.helper_funcs'
    events = 'userbot.events'
    for module in modules:
        if module.startswith((plugins, helper_funcs, events)):
            try:
                reload(modules[module])
            except Exception as e:
                msg = f"\nFailed to reload {module}. Ignoring."
                excp_msg = type(e) + ": " + e + "\n"
                LOGGER.warning(msg)
                def_text += "\n".join((msg, excp_msg))
                print(excp_msg)

    await c.restart()

    for handler in main_handlers:
        client.add_handler(*handler)

    LOGGER.warning("Successfully restarted the Pyrogram client.")
    LOGGER.warning(
        f"Successfully reloaded {len(main_handlers)} main command functions."
    )
    await event.edit(def_text)


@main_command("restart")
async def restart(c, event):
    loop.create_task(restarter(c, event))


@main_command("shutdown")
async def shutdown(c, event):
    await event.edit(
        "`Stopping the Pyrogram client and exiting the script.`"
    )
    loop.create_task(client.stop())
    print("\nUserBot script exiting.")
    exit()


@main_command(r"enable (\w+)")
async def enable(c, event):
    to_enable = event.matches[0].group(1).lower()
    handler = None
    command = None

    for command in disabled_commands:
        if command == to_enable:
            handler = disabled_commands[command]
            command = command
            break

    if handler and command:
        client.add_handler(*handler)
        del disabled_commands[command]
    else:
        await event.edit("`Can't enable something that's not disabled.`")
        return
    await event.edit(f"`Successfully enabled {command}.`")


@main_command(r"disable (\w+)")
async def disable(c, event):
    commands = bot_commands()
    to_disable = event.matches[0].group(1).lower()
    can_disable = None

    for command in commands:
        if command == to_disable and command not in disabled_commands:
            handler = commands[command]
            disabled_commands.update({command: handler})
            client.remove_handler(*handler)
            can_disable = True
            break

    if can_disable:
        text = f"**Successfully disabled {to_disable}.**"
    else:
        text = "`Couldn't find the specified command.`"
    await event.edit(text)


@main_command("disabled")
async def disabled(c, event):
    if disabled_commands:
        header = "**Disabled commands:**\n"
        commands = "\n".join(disabled_commands)
        text = header + commands
    else:
        text = "`There aren't any disabled commands.`"
    await event.edit(text)


@main_command("commands")
async def commands(c, event):
    commands = bot_commands()
    header = "**Available commands:**\n"
    com_list = "\n".join(commands)
    await event.edit(header + com_list)


async def main():
    await client.start()

    me = await client.get_me()
    if me.username:
        user = me.username
    else:
        user = me.first_name + " [" + me.id + "]"

    LOGGER.warning(f"Successfully loaded {len(main_handlers)} main functions.")
    print(__copyright__)
    print("Licensed under the terms of the " + __license__)
    print(
        "You're currently logged in as {0}{2}.{1}".format(CUSR, CEND, user)
    )
    print(
        "{0}UserBot v{2}{1} is running, test it by sending .ping in"
        " any chat.\n".format(CUSR, CEND, __version__)
    )

    await client.idle()


if __name__ == '__main__':
    loop.run_until_complete(main())
