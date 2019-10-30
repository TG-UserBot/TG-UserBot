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


from asyncio import sleep
from dataclasses import dataclass
import datetime
import os
import time
from telethon.events import StopPropagation
from telethon.tl import types
from telethon.utils import get_display_name
from typing import List, Tuple

from userbot import client
from userbot.utils.helpers import _humanfriendly_seconds

reason = None
pings = {}
privates = {}
groups = {}
sent = {}


@dataclass
class Chat:
    title: str
    unread_from: int
    mentions: List[int]


@client.onMessage(
    command="afk",
    outgoing=True, regex="afk(?: |$)(.*)?$"
)
async def awayfromkeyboard(event):
    """Set your status as AFK until you send a message again."""
    arg = event.matches[0].group(1)
    rn = time.time().__str__()
    os.environ.setdefault('userbot_afk', rn)
    text = "`I'm AFK!`"
    if arg:
        global reason
        reason = arg.strip()
        text += f"\n`Reason:` `{arg}`"
    log = "You just went AFK in [{}]({})!"
    chat = await event.get_chat()
    if isinstance(chat, types.User):
        link = f"tg://user?id={chat.id}"
    else:
        link = f"https://t.me/c/{chat.id}/{event.id}"
    await event.answer(
        text,
        log=("afk", log.format(get_display_name(chat), link))
    )
    raise StopPropagation


@client.onMessage(outgoing=True, forwards=True)
async def out_listner(event):
    """Handle your AFK status by listening to new outgoing messages."""
    if event.from_scheduled:
        return
    afk = os.environ.get('userbot_afk', False)
    if not afk:
        return

    def_text = "`You recieved no messages nor were tagged at any time.`"
    pr_text = ''
    pr_log = ''
    gr_text = ''
    gr_log = ''

    if privates:
        total_mentions = 0
        to_log = []
        pr_log = "**Mentions recieved from private chats:**\n"
        for key, value in privates.items():
            total_mentions += len(value.mentions)
            msg = "  `{} total mentions from `[{}](tg://user?id={})`.`"
            to_log.append(msg.format(len(value.mentions), value.title, key))

        pr_text = "`Recieved {} message{} from {} private chat{}.`".format(
            *(await _correct_grammer(total_mentions, len(privates)))
        )
        pr_log = pr_log + "\n".join("  " + t for t in to_log)
    if groups:
        total_mentions = 0
        to_log = []
        gr_log = "\n**Mentions recieved from groups:**\n"
        for key, value in groups.items():
            total_mentions += len(value.mentions)
            msg = f"[{value.title}](https://t.me/c/{key}/{value.unread_from}):"
            msg += "\n    `Mentions: `"
            mentions = []
            for i in range(len(value.mentions)):
                mentions.append(
                    f"[{i + 1}](https://t.me/c/{key}/{value.mentions[i]})"
                )
            msg += ',   '.join(mentions) + '.'
            to_log.append(msg)

        gr_text = "`Recieved {} mention{} from {} group{}.`".format(
            *(await _correct_grammer(total_mentions, len(groups)))
        )
        gr_log = gr_log + "\n".join("  " + t for t in to_log)

    main_text = '\n'.join([pr_text, gr_text]).strip()
    if not client.logger:
        main_text += "\n`Use a logger group for more detailed AFK mentions!`"
    status = await event.answer("`I am no longer AFK!`")
    toast = await event.answer(
        message=main_text or def_text,
        reply_to=status.id,
        log=("afk", '\n'.join([pr_log, gr_log]).strip() or def_text)
    )
    del os.environ['userbot_afk']

    global reason
    reason = None
    for chat, msg in sent.items():
        await client.delete_messages(chat, msg)
    privates.clear()
    groups.clear()
    sent.clear()
    await sleep(4)
    await toast.delete()
    await status.delete()


@client.onMessage(incoming=True, edited=False)
async def inc_listner(event):
    """Handle tags and new messages by listening to new incoming messages."""
    sender = await event.get_sender()
    if event.from_scheduled or (isinstance(sender, types.User) and sender.bot):
        return

    afk = os.environ.get('userbot_afk', False)
    if not (afk and (event.is_private or event.mentioned)):
        return

    since = datetime.datetime.fromtimestamp(
        float(afk),
        tz=datetime.timezone.utc
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    elapsed = await _humanfriendly_seconds((now - since).total_seconds())
    text = "`I am currently AFK{}.`\n`Last seen: {} ago.`".format(
        ' because ' + reason if reason else '', elapsed
    )

    chat = await event.get_chat()
    if event.is_private:
        await _append_msg(privates, chat.id, event.id)
    else:
        await _append_msg(groups, chat.id, event.id)

    if chat.id in sent:
        # Default timeout is 150 seconds / 2.5 minutes
        if round((now - sent[chat.id][-1].date).total_seconds()) <= 150:
            return

    result = await event.answer(message=text, reply_to=None)
    sent.setdefault(chat.id, []).append(result)


async def _append_msg(variable: dict, chat: int, event: int) -> None:
    if chat in variable:
        variable[chat].mentions.append(event)
    else:
        async for dialog in client.iter_dialogs():
            if chat == dialog.entity.id:
                title = getattr(dialog, 'title', dialog.name)
                unread_count = dialog.unread_count
                last_msg = dialog.message.id
                break
        x = 1
        messages = []
        async for message in client.iter_messages(
            chat,
            max_id=last_msg
        ):
            if x >= unread_count:
                if not messages:
                    messages.append(message.id)
                break
            if not message.out:
                x = x + 1
                messages.append(message.id)
        variable[chat] = Chat(title, messages[-1], [event])
        messages.clear()


async def _correct_grammer(mentions: int, chats: int) -> Tuple[str]:
    a1 = "one" if mentions == 1 else mentions
    a2 = '' if mentions == 1 else 's'
    a3 = "one" if chats == 1 else chats
    a4 = '' if chats == 1 else 's'
    return a1, a2, a3, a4
