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


import os.path
from typing import Tuple

from userbot import client
from userbot.utils.events import NewMessage


plugin_category: str = "helper"
link: str = "https://tg-userbot.readthedocs.io/en/latest/userbot/commands.html"
chunk: int = 5


@client.onMessage(
    command=("setprefix", plugin_category),
    outgoing=True, regex=r"setprefix (.+)", builtin=True
)
async def setprefix(event: NewMessage.Event) -> None:
    """Change the bot's default prefix."""
    match = event.matches[0].group(1).strip()
    old_prefix = client.prefix
    client.prefix = match
    client.config['userbot']['userbot_prefix'] = match
    if old_prefix is None:
        await event.answer(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**resetprefix**".format(client.prefix),
            log=("setprefix", f"Prefix changed to {client.prefix}")
        )
    else:
        await event.answer(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**{0}setprefix {1}**".format(
                client.prefix, old_prefix
            ),
            log=(
                "setprefix",
                f"prefix changed to {client.prefix} from {old_prefix}"
            )
        )
    client._updateconfig()


@client.onMessage(
    command=("resetprefix", plugin_category),
    outgoing=True, regex=r"(?i)^resetprefix$", disable_prefix=True,
    builtin=True
)
async def resetprefix(event: NewMessage.Event) -> None:
    """Reset the bot's prefix to the default ones."""
    prefix = client.config['userbot'].get('userbot_prefix', None)
    if prefix:
        del client.config['userbot']['userbot_prefix']
        client.prefix = None
        await event.answer(
            "`Successfully reset your prefix to the deafult ones!`",
            log=("resetprefix", "Successfully reset your prefix")
        )
        client._updateconfig()
    else:
        await event.answer(
            "`There is no prefix set as a default!`"
        )


@client.onMessage(
    command=("enable", plugin_category),
    outgoing=True, regex=r"enable(?: |$)(\w+)?$", builtin=True
)
async def enable(event: NewMessage.Event) -> None:
    """Enable a command IF it's already disabled."""
    arg = event.matches[0].group(1)
    if not arg:
        await event.answer("`Enable what? The void?`")
        return
    commands, command_list = await solve_commands(client.disabled_commands)
    command = commands.get(arg, False)
    if command:
        for handler in command.handlers:
            client.add_event_handler(command.func, handler)
        if arg in command_list:
            com = command_list.get(arg)
            client.commands[com] = command
            del client.disabled_commands[com]
            enabled_coms = ', '.join(com.split('/'))
        else:
            client.commands[arg] = command
            del client.disabled_commands[arg]
            enabled_coms = arg

        await event.answer(
            f"`Successfully enabled {enabled_coms}`",
            log=("enable", f"Enabled command(s): {enabled_coms}")
        )
    else:
        await event.answer(
            "`Couldn't find the specified command. "
            "Perhaps it's not disabled?`"
        )


@client.onMessage(
    command=("disable", plugin_category),
    outgoing=True, regex=r"disable(?: |$)(\w+)?$", builtin=True
)
async def disable(event: NewMessage.Event) -> None:
    """Disable a command IF it's already enabled."""
    arg = event.matches[0].group(1)
    if not arg:
        await event.answer("`Disable what? The void?`")
        return
    commands, command_list = await solve_commands(client.commands)
    command = commands.get(arg, False)
    if command:
        if command.builtin:
            await event.answer("`Cannot disable a builtin command.`")
        else:
            client.remove_event_handler(command.func)
            if arg in command_list:
                com = command_list.get(arg)
                client.disabled_commands[com] = command
                del client.commands[com]
                disabled_coms = ', '.join(com.split('/'))
            else:
                client.disabled_commands[arg] = command
                del client.commands[arg]
                disabled_coms = arg
            await event.answer(
                f"`Successfully disabled {disabled_coms}`",
                log=("disable", f"Disabled command(s): {disabled_coms}")
            )
    else:
        await event.answer("`Couldn't find the specified command.`")


@client.onMessage(
    command=("enabled", plugin_category),
    outgoing=True, regex="enabled$", builtin=True
)
async def commands(event: NewMessage.Event) -> None:
    """A list of all the currently enabled commands."""
    response = "**Enabled commands:**"
    commands, _ = await solve_commands(client.commands)
    enabled = sorted(commands.keys())
    for i in range(0, len(enabled), chunk):
        response += "\n  "
        response += ", ".join('`' + c + '`' for c in enabled[i:i+chunk])
    await event.answer(response)


@client.onMessage(
    command=("disabled", plugin_category),
    outgoing=True, regex="disabled$", builtin=True
)
async def disabled(event: NewMessage.Event) -> None:
    """A list of all the currently disabled commands."""
    disabled_commands, _ = await solve_commands(client.disabled_commands)

    if not disabled_commands:
        await event.answer("`There are no disabled commands currently.`")
        return

    response = "**Disabled commands:**"
    disabled = sorted(disabled_commands.keys())
    for i in range(0, len(disabled), chunk):
        response += "\n  "
        response += ", ".join('`' + c + '`' for c in disabled[i:i+chunk])
    await event.answer(response)


@client.onMessage(
    command=("help", plugin_category), builtin=True,
    outgoing=True, regex=r"help(?: |$)(\w*)(?: |$)(dev|details|info)?"
)
async def helper(event: NewMessage.Event) -> None:
    """A list of commands categories, their commands or command's details."""
    arg = event.matches[0].group(1)
    arg1 = event.matches[0].group(2)
    enabled, _ = await solve_commands(client.commands)
    disabled, _ = await solve_commands(client.disabled_commands)
    categories = client.commandcategories
    if arg:
        arg = arg.lower()
        if arg == "all":
            text = "**Enabled commands:**\n"
            if arg1:
                text += '\n\n'.join([
                    f'`{n}`: `{i.info}`' for n, i in sorted(enabled.items())
                ])
            else:
                text += ', '.join([f'`{name}`' for name in sorted(enabled)])
            if disabled:
                text += "\n**Disabled commands:**"
                if arg1:
                    text += '\n\n'.join([
                        f'`{n}`: `{i.info}`'
                        for n, i in sorted(disabled.items())
                    ])
                else:
                    text += ', '.join([
                        f'`{name}`' for name in sorted(disabled)
                    ])
        elif arg in [*enabled, *disabled]:
            merged = {**enabled, **disabled}
            command = merged.get(arg)
            text = (
                f"**{arg.title()} command:**\n"
                f"  **Disableable:** `{not command.builtin}`\n"
                f"  **Info:** `{command.info}`\n"
            )
            if arg1:
                filename = os.path.relpath(command.func.__code__.co_filename)
                text += (
                    f"  **Registered function:** `{command.func.__name__}`\n"
                    f"    **File:** `{filename}`\n"
                    f"    **Line:** `{command.func.__code__.co_firstlineno}`\n"
                )
        elif arg in categories:
            category = categories.get(arg)
            text = f"**{arg.title()} commands:**"
            for com in sorted(category):
                text += f"\n    **{com}**"
        else:
            await event.answer(
                "`Couldn't find the specified command or command category!`"
            )
            return
    else:
        text = (
            f"Documented commands can be found [HERE!]({link})\n"
            f"**Usage:**\n"
            f"  __{client.prefix or '.'}help <category>__\n"
            f"  __{client.prefix or '.'}help <command>__\n"
            f"  __{client.prefix or '.'}help all__\n\n"
            "**Available command categories:**"
        )
        for category in sorted(categories.keys()):
            text += f"\n    **{category}**"
    await event.answer(text)


async def solve_commands(commands: dict) -> Tuple[dict, dict]:
    new_dict: dict = {}
    com_tuples = {}
    for com_names, command in commands.items():
        if '/' in com_names:
            for n in com_names.split('/'):
                com_tuples[n] = com_names
                new_dict[n] = command
        else:
            new_dict[com_names] = command
    return new_dict, com_tuples
