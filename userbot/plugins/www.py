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


plugin_category = "www"
DCs = {
    1: "149.154.175.50",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.149"
}


@client.onMessage(
    command=("ping", plugin_category),
    outgoing=True, regex="ping$"
)
async def ping(event):
    """Check how long it takes to get an update and respond to it."""
    start = datetime.now()
    await event.answer("**PONG**")
    duration = (datetime.now() - start)
    milliseconds = duration.microseconds / 1000
    await event.answer(f"**PONG:** `{milliseconds}ms`")


@client.onMessage(
    command=("nearestdc", plugin_category),
    outgoing=True, regex="nearestdc$"
)
async def nearestdc(event):
    """Get information of your country and data center information."""
    result = await client(GetNearestDcRequest())
    text = (
        f"**Country:** `{result.country}`\n" +
        f"**This DC:** `{result.this_dc}`\n" +
        f"**Nearest DC:** `{result.nearest_dc}`"
    )
    await event.answer(text)


@client.onMessage(
    command=("pingdc", plugin_category),
    outgoing=True, regex=r"pingdc(?: |$)(\d+)?"
)
async def pingdc(event):
    """Ping your or other data center's IP addresses."""
    if event.matches[0].group(1) in ('1', '2', '3', '4', '5'):
        dc = int(event.matches[0].group(1))
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
        await event.answer(err)
        return
    await event.answer(f"DC {dc}'s average response: `{average}`")


async def _sub_shell(cmd):
    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    return stdout.decode("UTF-8"), stderr.decode("UTF-8")
