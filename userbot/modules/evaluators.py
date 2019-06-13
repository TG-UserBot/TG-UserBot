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
from asyncio import create_subprocess_exec, create_subprocess_shell,\
                    subprocess

from userbot import client
from userbot.events import message
from userbot.helper_funcs.messages import limit_exceeded


@message(outgoing=True, pattern=r"^.eval(?: |$)([\s\S]*)")
async def evaluate(event):
    expression = event.pattern_match.group(1).strip()
    reply = await event.get_reply_message()
    if not expression:
        await event.edit("Evaluating the void...")
        return
    
    try:
        result = eval(expression, {'client': client, 'event': event, 'reply': reply})
        if isawaitable(result):
            result = await result
        result = str(result)
        if (len(result)) > 4096:
            await event.edit("Output was too big, result can be viewed from the file.")
            await limit_exceeded(result, event.chat_id, event)
            return
    except Exception as e:
        await event.edit(type(e).__name__ + ': ' + str(e))
        return

    await event.edit(result)


@message(outgoing=True, pattern=r"^.exec(?: |$)([\s\S]*)")
async def execute(event):
    code = event.pattern_match.group(1).strip()
    if not code:
        await event.edit("Executing the void...")
        return

    await event.edit("Executing your code...")
    process = await create_subprocess_exec(
        executable, '-c', code,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    extras = f"[**PID:** `{process.pid}`] [**Return code:** `{process.returncode}`]\n\n"

    if stderr:
        text = ("__You dun goofed up.__" + extras + stderr.decode('UTF-8'))
        await event.edit(text)
        return

    elif stdout:
        text = stdout.decode("UTF-8")
        if (len(text) + len(extras)) > 4096:
            await event.edit("Output was too big, result can be viewed from the file.")
            await limit_exceeded(extras + text, event.chat_id, event)
            return
        await event.edit(extras + text)
    else:
        await event.edit(extras + "Nice, get off the void.")


@message(outgoing=True, pattern=r"^.term(?: |$)([\s\S]*)")
async def terminal(event):
    cmd = event.pattern_match.group(1).strip()
    if not cmd:
        await event.edit("Executing the void...")
        return

    await event.edit("Executing your command...")
    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    extras = f"[**PID:** `{process.pid}`] [**Return code:** `{process.returncode}`]\n\n"

    if stderr:
        text = ("__You dun goofed up.__" + extras + stderr.decode('UTF-8'))
        await event.edit(text)
        return

    elif stdout:
        text = stdout.decode("UTF-8")
        if (len(text) + len(extras)) > 4096:
            await event.edit("Output was too big, result can be viewed from the file.")
            await limit_exceeded(extras + text, event.chat_id, event)
            return
        await event.edit(extras + text)
    else:
        await event.edit(extras + "Nice, get off the void.")