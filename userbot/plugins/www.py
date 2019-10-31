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
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from speedtest import Speedtest
from sys import platform
from telethon.tl.functions.help import GetNearestDcRequest

from userbot import client
from userbot.utils.helpers import get_chat_link


plugin_category = "www"
loop = client.loop
DCs = {
    1: "149.154.175.50",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.149"
}
testing = "`Testing from %(isp)s (%(ip)s)`"
hosted = "`Hosted by %(sponsor)s (%(name)s) [%(d)0.2f km]: %(latency)s ms`"
download = "`Download: %0.2f M%s/s`"
upload = "`Upload: %0.2f M%s/s`"


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


@client.onMessage(
    command=("speedtest", plugin_category),
    outgoing=True, regex=r"speedtest(?: |$)(bit|byte)?$"
)
async def speedtest(event):
    """Perform a speedtest with the best available server based on ping."""
    n = 1
    unit = "bit"
    arg = event.matches[0].group(1)
    if arg and arg.lower() == "byte":
        n = 8
        unit = "byte"

    s = Speedtest()
    speed_event = await event.answer(testing % s.results.client)
    await _run_sync(s.get_servers)

    await _run_sync(s.get_best_server)
    text = (f"{speed_event.text}\n{hosted % s.results.server}")
    speed_event = await event.answer(text)

    await _run_sync(s.download)
    down = (s.results.download / 1000.0 / 1000.0) / n
    text = (f"{speed_event.text}\n{download % (down, unit)}")
    speed_event = await event.answer(text)

    await _run_sync(s.upload)
    up = (s.results.upload / 1000.0 / 1000.0) / n
    text = (f"{speed_event.text}\n{upload % (up, unit)}")
    extra = await get_chat_link(event, event.id)
    await event.answer(
        text,
        log=("speedtest", f"Performed a speedtest in {extra}.")
    )


async def _sub_shell(cmd):
    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    return stdout.decode("UTF-8"), stderr.decode("UTF-8")


async def _run_sync(func: callable):
    return await loop.run_in_executor(ThreadPoolExecutor(), func)
