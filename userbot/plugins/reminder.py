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


from asyncio import sleep, create_task
from telethon.tl.functions.messages import ToggleDialogPinRequest

from userbot import client
from userbot.helper_funcs.time import string_to_secs


@client.onMessage(
    command="remindme", info="Recieve a reminder in your saved messages",
    outgoing=True, regex=r"remindme (\w+) ([\s\S]*)"
)
async def remindme(event):
    """Remind me function used to create a reminder for .remindme"""
    time = event.matches[0].group(1)
    text = event.matches[0].group(2)
    seconds = await string_to_secs(time)

    if seconds != 0:
        create_task(
            _reminderTask(seconds, text)
        )
        text = f"`Reminder will be sent in Saved Messages after {time}.`"
        if seconds >= 86400:
            text += (
                "`\nThis may not work as expected, not fully certain though.`"
            )
        await event.edit(text)
    else:
        await event.edit("`No kan do. ma'am.`")


@client.onMessage(
    command="dismiss", info="Dismiss the reminder in your saved messages",
    outgoing=True, regex=r"(?i)^dismiss$", disable_prefix=True
)
async def dismiss(event):
    """Dismiss function used to delete and unpin dialogs for dismiss"""
    reply = await event.get_reply_message()
    if reply:
        await reply.delete()
    await event.delete()

    await client(
        ToggleDialogPinRequest(peer="self", pinned=None)
    )


async def _reminderTask(delay, string):
    """Reminder task function used to send the reminder after sleep."""
    await sleep(delay)
    await client(
        ToggleDialogPinRequest(peer="self", pinned=True)
    )
    await client.send_message("self", string)
