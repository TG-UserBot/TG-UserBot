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


from os.path import relpath

from userbot import client

plugin_category = "helper"
link = "https://tg-userbot.readthedocs.io/en/latest/userbot/commands.html"
chunk: int = 5


@client.onMessage(
    command=("setprefix", plugin_category),
    outgoing=True, regex=r"setprefix (.+)", builtin=True
)
async def setprefix(event):
    """Change the bot's default prefix."""
    match = event.matches[0].group(1).strip()
    old_prefix = client.prefix
    event.client.prefix = match
    event.client.config['userbot']['prefix'] = match
    if old_prefix is None:
        await event.answer(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**resetprefix**".format(event.client.prefix),
            log=("setprefix", f"Prefix changed to {event.client.prefix}")
        )
    else:
        await event.answer(
            "`Successfully changed the prefix to `**{0}**`. "
            "To revert this, do `**{0}setprefix {1}**".format(
                event.client.prefix, old_prefix
            ),
            log=(
                "setprefix",
                f"prefix changed to {event.client.prefix} from {old_prefix}"
            )
        )
    client._updateconfig()


@client.onMessage(
    command=("resetprefix", plugin_category),
    outgoing=True, regex=r"(?i)^resetprefix$", disable_prefix=True,
    builtin=True
)
async def resetprefix(event):
    """Reset the bot's prefix to the default ones."""
    prefix = event.client.config['userbot'].get('prefix', None)
    if prefix:
        del client.config['userbot']['prefix']
        event.client.prefix = None
        await event.answer(
            "`Succesffully reset your prefix to the deafult ones!`",
            log=("resetprefix", "Successfully reset your prefix")
        )
        client._updateconfig()
    else:
        await event.answer(
            "`There is no prefix set as a default!`"
        )


@client.onMessage(
    command=("enable", plugin_category),
    outgoing=True, regex=r"enable (\w+)$", builtin=True
)
async def enable(event):
    """Enable a command IF it's already disabled."""
    command = event.matches[0].group(1)
    if event.client.disabled_commands.get(command, False):
        com = event.client.disabled_commands.get(command)
        for handler in com.handlers:
            event.client.add_event_handler(com.func, handler)
        event.client.commands.update({command: com})
        del event.client.disabled_commands[command]
        await event.answer(
            f"`Successfully enabled {command}`",
            log=("enable", f"Enabled command: {command}")
        )
    else:
        await event.answer(
            "`Couldn't find the specified command. "
            "Perhaps it's not disabled?`"
        )


@client.onMessage(
    command=("disable", plugin_category),
    outgoing=True, regex=r"disable (\w+)$", builtin=True
)
async def disable(event):
    """Disable a command IF it's already enabled."""
    command = event.matches[0].group(1)
    if event.client.commands.get(command, False):
        com = event.client.commands.get(command)
        if com.builtin:
            await event.answer("`Cannot disable a builtin command.`")
        else:
            event.client.remove_event_handler(com.func)
            event.client.disabled_commands.update({command: com})
            del event.client.commands[command]
            await event.answer(
                f"`Successfully disabled {command}`",
                log=("disable", f"Disabled command: {command}")
            )
    else:
        await event.answer("`Couldn't find the specified command.`")


@client.onMessage(
    command=("enabled", plugin_category),
    outgoing=True, regex="enabled$", builtin=True
)
async def commands(event):
    """A list of all the currently enabled commands."""
    response = "**Enabled commands:**"
    enabled = sorted(event.client.commands.keys())
    for i in range(0, len(enabled), chunk):
        response += "\n  "
        response += ", ".join('`' + c + '`' for c in enabled[i:i+chunk])
    await event.answer(response)


@client.onMessage(
    command=("disabled", plugin_category),
    outgoing=True, regex="disabled$", builtin=True
)
async def disabled(event):
    """A list of all the currently disabled commands."""
    disabled_commands = event.client.disabled_commands

    if not disabled_commands:
        await event.answer("`There are no disabled commands currently.`")
        return

    response = "**Disabled commands:**"
    enabled = sorted(disabled_commands.keys())
    for i in range(0, len(enabled), chunk):
        response += "\n  "
        response += ", ".join('`' + c + '`' for c in enabled[i:i+chunk])
    await event.answer(response)


@client.onMessage(
    command=("help", plugin_category), builtin=True,
    outgoing=True, regex=r"help(?: |$)(.*)?"
)
async def helper(event):
    """A list of commands categories, their commands or command's details."""
    arg = event.matches[0].group(1)
    enabled = event.client.commands
    disabled = event.client.disabled_commands
    categories = event.client.commandcategories
    if arg:
        arg = arg.strip().lower()
        arg1 = True if arg.endswith(("dev", "details", "info")) else False
        if arg1:
            arg = ' '.join(arg.split(' ')[:-1])
        if arg == "all":
            text = "**Enabled commands:**"
            for name, command in sorted(enabled.items()):
                text += f"\n**{name}**: `{command.info}`"
            if disabled:
                text += "\n**Disabled commands:**"
                for name, command in sorted(disabled.items()):
                    text += f"\n**{name}**: `{command.info}`"
        elif arg in [*enabled, *disabled]:
            merged = {**enabled, **disabled}
            command = merged.get(arg)
            text = (
                f"**{arg.title()} command:**\n"
                f"  **Disableable:** `{not command.builtin}`\n"
                f"  **Info:** `{command.info}`\n"
            )
            if arg1:
                filename = relpath(command.func.__code__.co_filename)
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
