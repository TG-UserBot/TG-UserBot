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

plugin_category = "user"


@client.onMessage(
    command=("remindme", plugin_category),
    outgoing=True, regex=r"remindme(?: |$)(\w+)?(?: |$)([\s\S]*)"
)
async def remindme(event):
    """Set a reminder to be sent to your Saved Messages in x amount of time."""
    time = event.matches[0].group(1)
    text = event.matches[0].group(2)
    if not time:
        await event.answer("Remind you with what?")
        return

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
        await event.answer(
            text,
            log=("remindme", f"Set a reminder. ETA: {time}")
        )
    else:
        await event.answer("`No kan do. ma'am.`")


@client.onMessage(
    command=("dismiss", plugin_category),
    outgoing=True, regex=r"(?i)^dismiss$", disable_prefix=True
)
async def dismiss(event):
    """Dismiss the current pinned message in Saved Messages."""
    reply = await event.get_reply_message()
    if reply:
        await reply.delete()
    await event.delete()

    await client.pin_message(event.chat_id, message=None)


async def _reminderTask(delay, string):
    """Reminder task function used to send the reminder after sleep."""
    await sleep(delay)
    await client(
        ToggleDialogPinRequest(peer="self", pinned=True)
    )
    await client.send_message("self", string)
