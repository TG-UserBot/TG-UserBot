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


from asyncio import create_subprocess_shell, subprocess
from datetime import datetime
from sys import platform
from telethon.tl.functions.help import GetNearestDcRequest

from userbot import client


DCs = {
    1: "149.154.175.50",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.149"
}


@client.onMessage(
    command="ping", info="Get message ping",
    outgoing=True, regex="ping$"
)
async def ping(event):
    """Ping function used to edit the message for .ping"""
    start = datetime.now()
    await event.edit("**PONG**")
    duration = (datetime.now() - start)
    milliseconds = duration.microseconds / 1000
    await event.edit(f"**PONG**\n`{milliseconds}ms`")


@client.onMessage(
    command="pingdc", info="Ping TG DCs",
    outgoing=True, regex=r"pingdc(?: |$)(\d+)?"
)
async def pingdc(event):
    """Ping DC function used to ping DC via shell for .pingdc"""
    if event.matches[0].group(1) in ('1', '2', '3', '4', '5'):
        dc = int(event.pattern_match.group(1))
    else:
        raw_dc = await client(GetNearestDcRequest())
        dc = raw_dc.this_dc
    param = "-n" if platform.startswith("win") else "-c"
    cmd = f"ping {param} 1 {DCs[dc]}"

    if platform.startswith("win"):
        out, err = await _sub_shell(cmd)
        average = out.split("Average = ")[1]
    else:
        out, err = await _sub_shell(cmd + " | awk -F '/' 'END {print $5}'")
        average = (out.strip() + "ms")
    if err:
        await event.edit(err)
        return
    await event.edit(f"DC {dc}'s average response: `{average}`")


@client.onMessage(
    command="setprefix", info="Change the current prefix of commands.",
    outgoing=True, regex=r"setprefix (.+)"
)
async def setprefix(event):
    """Change the prefix default prefix."""
    old_prefix = client.prefix
    client.prefix = event.matches[0].group(1).strip()
    await event.edit(
        "`Successfully changed the prefix to `**{0}**`. "
        "To revert this, do `**{0}setprefix {1}**".format(
            client.prefix, old_prefix
        )
    )


@client.onMessage(
    command="shutdown", info="Disconnect the client and exit the script.",
    outgoing=True, regex="shutdown$", builtin=True
)
async def shutdown(event):
    """Shutdown userbot."""
    await event.edit("`Disconnecting the client and exiting. Ciao!`")
    await event.client.disconnect()


@client.onMessage(
    command="restart", info="Restart the client and reimport plugins.",
    outgoing=True, regex="restart$", builtin=True
)
async def restart(event):
    """Restart userbot."""
    event.client.loop.create_task(event.client._restarter(event))


@client.onMessage(
    command="enable", info="Enable a disabled command.",
    outgoing=True, regex=r"enable (\w+)$", builtin=True
)
async def enable(event):
    command = event.matches[0].group(1)
    if event.client.disabled_commands.get(command, False):
        com = event.client.disabled_commands.get(command)
        for handler in com.handlers:
            event.client.add_event_handler(com.func, handler)
        event.client.commands.update({command: com})
        del event.client.disabled_commands[command]
        await event.edit(f"`Successfully enabled {command}`")
    else:
        await event.edit(
            "`Couldn't find the specified command. "
            "Perhaps it's not disabled?`"
        )


@client.onMessage(
    command="disable", info="Disable an enabled command.",
    outgoing=True, regex=r"disable (\w+)$", builtin=True
)
async def disable(event):
    command = event.matches[0].group(1)
    if event.client.commands.get(command, False):
        com = event.client.commands.get(command)
        if com.builtin:
            await event.edit("`Cannot disable a builtin command.`")
        else:
            event.client.remove_event_handler(com.func)
            event.client.disabled_commands.update({command: com})
            del event.client.commands[command]
            await event.edit(f"`Successfully disabled {command}`")
    else:
        await event.edit("`Couldn't find the specified command.`")


@client.onMessage(
    command="commands", info="Lists all the enabled commands.",
    outgoing=True, regex=r"commands$", builtin=True
)
async def commands(event):
    response = "**Enabled commands:**"
    for name, command in event.client.commands.items():
        response += f"\n**{name}:** `{command.info}`"
    await event.edit(response)


@client.onMessage(
    command="disabled", info="Lists all the disabled commands.",
    outgoing=True, regex=r"disabled$", builtin=True
)
async def disabled(event):
    disabled_commands = event.client.disabled_commands

    if not disabled_commands:
        await event.edit("`There are no disabled commands currently.`")
        return

    response = "**Disabled commands:**"
    for name, command in disabled_commands.items():
        response += f"\n**{name}:** `{command.info}`"
    await event.edit(response)


async def _sub_shell(cmd):
    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    return stdout.decode("UTF-8"), stderr.decode("UTF-8")
