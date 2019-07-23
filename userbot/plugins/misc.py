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
from pyrogram.api.functions.help import GetNearestDc

from userbot.events import outgoing


DCs = {1: "149.154.175.50", 2: "149.154.167.51",
    3: "149.154.175.100", 4: "149.154.167.91", 5: "91.108.56.149"}


@outgoing(pattern="ping$")
async def ping(client, event):
    start = datetime.now()
    await event.edit("**PONG**")
    duration = (datetime.now() - start)
    milliseconds = duration.microseconds / 1000
    await event.edit(f"**PONG**\n`{milliseconds}ms`")


@outgoing(pattern=r"pingdc(?: |$)(\d+)?")
async def pingdc(client, event):
    if event.matches[0].group(1) in ("1", "2", "3", "4", "5"):
        dc = int(event.matches[0].group(1))
    else:
        raw_dc = await client.send(GetNearestDc())
        dc = raw_dc.this_dc
    param = "-n" if platform.startswith('win') else "-c"
    cmd = f"ping {param} 1 {DCs[dc]}"
    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if stderr:
        await event.edit(stderr)
        return
    average = stdout.decode("UTF-8").split("Average = ")[1]
    await event.edit(f"DC {dc}'s average response: `{average}`")