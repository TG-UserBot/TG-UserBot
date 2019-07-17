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


from sys import executable
from inspect import isawaitable
from asyncio import (create_subprocess_exec, create_subprocess_shell,
    subprocess)

from userbot.events import outgoing
from userbot.helper_funcs.messages import limit_exceeded


@outgoing(pattern=r"eval(?: |$)([\s\S]*)")
async def evaluate(client, event):
    expression = event.matches[0].group(1).strip()
    reply = event.reply_to_message
    if not expression:
        await event.edit("Evaluated the void.")
        return
    
    try:
        result = eval(
            expression, {'client': client, 'event': event, 'reply': reply}
        )
        if isawaitable(result):
            result = await result
        result = str(result)
        if (len(result)) > 4096:
            await limit_exceeded(event, result, True)
            return
    except Exception as e:
        await event.reply(type(e).__name__ + ': ' + str(e))
        return

    await event.reply(result)


@outgoing(pattern=r"exec(?: |$)([\s\S]*)")
async def execute(client, event):
    code = event.matches[0].group(1).strip()
    if not code:
        await event.edit("Executed the void.")
        return

    process = await create_subprocess_exec(
        executable, '-c', code,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    extras = (f"[**PID:** `{process.pid}`] "
        f"[**Return code:** `{process.returncode}`]\n\n")

    if stderr:
        text = ("__You dun goofed up.__\n" + extras + stderr.decode('UTF-8'))
        await event.reply(text)
        return

    elif stdout:
        text = stdout.decode("UTF-8")
        if (len(text) + len(extras)) > 4096:
            await limit_exceeded(event, extras + text, True)
            return
        await event.reply(extras + text)
    else:
        await event.reply(extras + "Nice, get off the void.")


@outgoing(pattern=r"term(?: |$)([\s\S]*)")
async def terminal(client, event):
    cmd = event.matches[0].group(1).strip()
    if not cmd:
        await event.edit("Executed the void.")
        return

    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    extras = (f"[**PID:** `{process.pid}`] "
        f"[**Return code:** `{process.returncode}`]\n\n")

    if stderr:
        text = ("__You dun goofed up.__\n" + extras + stderr.decode('UTF-8'))
        await event.reply(text)
        return

    elif stdout:
        text = stdout.decode("UTF-8")
        if (len(text) + len(extras)) > 4096:
            await limit_exceeded(event, extras + text, True)
            return
        await event.reply(extras + text)
    else:
        await event.reply(extras + "Nice, get off the void.")