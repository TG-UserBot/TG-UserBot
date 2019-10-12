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


from sys import executable
from inspect import isawaitable
from asyncio import (
    create_subprocess_exec, create_subprocess_shell, subprocess, sleep
)

from userbot import client
from userbot.helper_funcs.messages import limit_exceeded


@client.onMessage(
    command="eval", info="Evaluate something",
    outgoing=True, regex=r"eval(?: |$)([\s\S]*)"
)
async def evaluate(event):
    """Evaluator function used to evaluate for .eval"""
    expression = event.matches[0].group(1).strip()
    reply = await event.get_reply_message()
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
            await limit_exceeded(event, "```" + result + "```", True)
            return
    except Exception as e:
        await event.reply('`' + type(e).__name__ + ': ' + str(e) + '`')
        return

    await event.reply("```" + result + "```")


@client.onMessage(
    command="exec", info="Excecute something",
    outgoing=True, regex=r"exec(?: |$)([\s\S]*)"
)
async def execute(event):
    """Executor function used to execute Python code for .exec"""
    message = (
        str(getattr(event.chat, 'id', event.chat_id)) +
        ':' +
        str(event.message.id)
    )
    if client.running_processes.get(message, False):
        await event.reply("A process for this event is already running!")
        return

    code = event.matches[0].group(1).strip()
    if not code:
        await event.edit("Executed the void.")
        return

    process = await create_subprocess_exec(
        executable, '-c', code,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    client.running_processes.update({
        message: process
    })
    stdout, stderr = await process.communicate()

    not_killed = client.running_processes.get(message, False)
    if not_killed:
        del client.running_processes[message]

    text = f"[EXEC] Return code: {process.returncode}\n"

    if stdout:
        text += "\n[stdout]\n" + stdout.decode("UTF-8").strip() + "\n"
    if stderr:
        text += "\n[stderr]\n" + stderr.decode('UTF-8').strip() + "\n"

    if stdout or stderr:
        if len(text) > 4096:
            await limit_exceeded(event, "```" + text + "```", True)
            return
        await event.reply("```" + text + "```")
    else:
        await event.reply("Nice, get off the void.\nNo output for you.")


@client.onMessage(
    command="term", info="Execute something in the terminal",
    outgoing=True, regex=r"term(?: |$)([\s\S]*)"
)
async def terminal(event):
    """Terminal function used to execute shell commands for .term"""
    message = (
        str(getattr(event.chat, 'id', event.chat_id)) +
        ':' +
        str(event.message.id)
    )
    if client.running_processes.get(message, False):
        await event.reply("A process for this event is already running!")
        return

    cmd = event.matches[0].group(1).strip()
    if not cmd:
        await event.edit("Executed the void.")
        return

    process = await create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    client.running_processes.update({
        message: process
    })
    stdout, stderr = await process.communicate()

    not_killed = client.running_processes.get(message, False)
    if not_killed:
        del client.running_processes[message]

    text = f"[TERM] Return code: {process.returncode}\n"

    if stdout:
        text += "\n[stdout]\n" + stdout.decode("UTF-8").strip() + "\n"
    if stderr:
        text += "\n[stderr]\n" + stderr.decode('UTF-8').strip() + "\n"

    if stdout or stderr:
        if len(text) > 4096:
            await limit_exceeded(event, "```" + text + "```", True)
            return
        await event.reply("```" + text + "```")
    else:
        await event.reply("Nice, get off the void.\nNo output for you.")


@client.onMessage(
    command="kill/terminate",
    outgoing=True, regex=r"(kill|terminate)$",
    info="Kill or Terminate a subprocess which is still running"
)
async def killandterminate(event):
    """Function used to kill or terminate asyncio subprocesses"""
    if not event.reply_to_msg_id:
        await event.edit(
            "`Reply to a message to kill or terminate the process!`"
        )
        return

    reply = await event.get_reply_message()
    message = (
        str(getattr(reply.chat, 'id', reply.chat_id)) + ':' + str(reply.id)
    )
    running_process = client.running_processes.get(message, False)

    if running_process:
        # If we ever want to wait for it to complete. (Most likely never)
        """try:
            await running_process.wait()
        finally:
            if running_process.returncode is None:"""

        option = event.matches[0].group(1)
        if option == "kill":
            running_process.kill()
        else:
            running_process.terminate()
        await event.edit(
            f"`Successfully {option}ed the process.`"
        )
        await sleep(2)
        await event.delete()
    else:
        await event.edit("`There is no process running for this message.`")
