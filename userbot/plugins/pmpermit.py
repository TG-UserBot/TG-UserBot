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


import datetime
import dill
import re
from asyncio import sleep
from typing import Dict, List

from telethon.tl import functions, types

from userbot import client, LOGGER
from userbot.utils.helpers import get_chat_link
from userbot.utils.events import NewMessage
from userbot.utils.sessions import RedisSession


plugin_category = "pmpermit"
PM_PERMIT = client.config['userbot'].getboolean('pm_permit', False)
if isinstance(type(client.session), type(RedisSession)):
    redis = client.session.redis_connection
else:
    redis = None

approvedUsers: List[int] = []
spammers: Dict[int, tuple] = {}

PP_UNAPPROVED_MSG = (
    "`Bleep blop! This is a bot. Don't fret.\n\n`"
    "`My master hasn't approved you to PM.`"
    "`Please wait for my master to look in, he mostly approves PMs.\n\n`"
    "`As far as I know, he doesn't usually approve retards though.`"
)
FTG_UNAPPROVED_MSG = (
    "Hey there! Unfortunately, I don't accept private messages from "
    "strangers.\n\nPlease contact me in a group, or **wait** "
    "for me to approve you."
)

warning = (
    "**You have one message left, you'll be reported and blocked upon "
    "sending the next message!**"
)
default = (
    "**This is an automated message, kindly wait until you're approved.**\n"
    "__You have {} remaining messages.__"
)
samedefault = "__You have {} remaining messages.__"
newdefault = (
    "**This is an automated message, kindly wait until you've been approved "
    "otherwise you'll be reported and blocked for spamming.**\n\n"
    "__You have {} remaining messages.__"
)
esc_default = re.escape(default.format(r'\d')).replace(r'\\d', r'\d')
esc_samedefault = re.escape(samedefault.format(r'\d')).replace(r'\\d', r'\d')
esc_newdefault = re.escape(newdefault.format(r'\d')).replace(r'\\d', r'\d')

blocked = "**You've been blocked and reported for spamming.**"
blocklog = "{} **has been blocked, unblock them to see their messages.**"
autoapprove = "**Successfully auto-approved** {}"

DEFAULT_MUTE_SETTINGS = types.InputPeerNotifySettings(
    silent=True,
    mute_until=datetime.timedelta(days=365)
)
DEFAULT_UNMUTE_SETTINGS = types.InputPeerNotifySettings(
    show_previews=True,
    silent=False
)

if redis:
    if redis.exists('approved:users'):
        approvedUsers = dill.loads(redis.get('approved:users'))


@client.onMessage(incoming=True, edited=False)
async def pm_incoming(event: NewMessage.Event) -> None:
    """Filter incoming messages for blocking."""
    if not PM_PERMIT or not redis or not event.is_private:
        return
    out = None
    new_pm = False
    entity = await event.get_sender()
    input_entity = await event.get_input_sender()
    sender = getattr(event, 'from_id', entity.id)

    if entity.mutual_contact:
        if sender not in approvedUsers:
            approvedUsers.append(sender)
            await update_db()
            user = await get_chat_link(entity)
            text = autoapprove.format(user) + " **for being a mutual contact.**"
            out = await event.answer(text, reply=True, log=('pmpermit', text))
            await sleep(2)
            await out.delete()
        return
    elif (
        entity.verified or entity.support or entity.bot or
        sender in approvedUsers
    ):
        return
    elif sender not in spammers:
        await client(functions.account.UpdateNotifySettingsRequest(
            peer=input_entity.user_id,
            settings=DEFAULT_MUTE_SETTINGS
        ))

    lastmsg, count, sent, lastoutmsg = spammers.setdefault(
        sender, (None, 5, [], None)
    )
    if count == 0:
        user = await get_chat_link(entity)
        await client.delete_messages(input_entity, sent)
        await client(functions.messages.ReportSpamRequest(
            peer=input_entity
        ))
        await client(functions.contacts.BlockRequest(
            id=input_entity
        ))
        await event.answer(blocked, log=('pmpermit', blocklog.format(user)))
        spammers.pop(sender, None)
        return

    if not lastmsg:
        result = await client.get_messages(
            input_entity, reverse=True, limit=1
        )
        if result[0].id == event.id:
            new_pm = True
    if lastoutmsg:
        await client.delete_messages(input_entity, [lastoutmsg])
    lastoutmsg = None

    if new_pm:
        out = await event.answer(newdefault.format(count))
    else:
        if count == 1:
            out = await event.answer(warning)
        elif (
            event.text in [PP_UNAPPROVED_MSG, FTG_UNAPPROVED_MSG] or
            re.search(esc_newdefault, event.text) or
            re.search(esc_default, event.text) or
            re.search(esc_samedefault, event.text)
        ):
            pass
        elif lastmsg and event.text == lastmsg:
            out = await event.answer(samedefault.format(count))
            lastoutmsg = out.id
        else:
            out = await event.answer(default.format(count))

    if not lastoutmsg and out:
        sent.append(out.id)
    spammers[sender] = (event.text, count-1, sent, lastoutmsg)


@client.onMessage(outgoing=True, edited=False)
async def pm_outgoing(event: NewMessage.Event) -> None:
    """Filter outgoing messages for auto-approving."""
    if (
        not PM_PERMIT or not redis or not event.is_private or
        event.chat_id in approvedUsers
    ):
        return
    chat = await event.get_chat()
    if chat.verified or chat.support or chat.bot:
        return

    result = await client.get_messages(
        await event.get_input_chat(), reverse=True, limit=1
    )
    if result[0].out:
        if chat.id not in approvedUsers:
            approvedUsers.append(chat.id)
            await update_db()
            user = await get_chat_link(chat)
            text = autoapprove.format(user)
            out = await event.answer(text, reply=True, log=('pmpermit', text))
            await sleep(2)
            await out.delete()


@client.onMessage(
    command=("approve", plugin_category),
    outgoing=True, regex=r"approve(?: |$)(.+)?$"
)
async def approve(event: NewMessage.Event) -> None:
    """Approve an user for PM-Permit."""
    if not PM_PERMIT or not redis:
        await event.answer("PM-Permit is disabled.")
        return
    user = await get_user(event)
    if user:
        if user.verified or user.support or user.bot:
            await event.answer(
                "__You don't need to approve bots or verified/support users.__"
            )
            return
        href = await get_chat_link(user)
        if user.id in approvedUsers:
            await event.answer(f"{href} __is already approved.__")
        else:
            approvedUsers.append(user.id)
            await update_db()
            text = f"__Successfully approved__ {href}"
            await event.answer(text, log=('pmpermit', text))
        if user.id in spammers:
            _, _, sent, _ = spammers.pop(user.id)  # Reset the counter
            await client.delete_messages(user, sent)
            await client(functions.account.UpdateNotifySettingsRequest(
                peer=user.id,
                settings=DEFAULT_UNMUTE_SETTINGS
            ))


@client.onMessage(
    command=("unapprove", plugin_category),
    outgoing=True, regex=r"(?:un|dis)approve(?: |$)(.+)?$"
)
async def disapprove(event: NewMessage.Event) -> None:
    """Disapprove an user for PM-Permit."""
    if not PM_PERMIT or not redis:
        await event.answer("PM-Permit is disabled.")
        return
    user = await get_user(event)
    if user:
        href = await get_chat_link(user)
        if user.id in approvedUsers:
            approvedUsers.remove(user.id)
            await update_db()
            text = f"__Successfully disapproved__ {href}"
            await event.answer(text, log=('pmpermit', text))
        else:
            await event.answer(f"{href} __hasn't been approved.__")
        spammers.pop(user.id, None)  # Reset the counter


@client.onMessage(
    command=("block", plugin_category),
    outgoing=True, regex=r"block(?: |$)(.+)?$"
)
async def block(event: NewMessage.Event) -> None:
    """Block an user and remove them from approved users."""
    result = False
    user = await get_user(event)
    if user:
        href = await get_chat_link(user)
        try:
            result = await client(functions.contacts.BlockRequest(
                id=user.id
            ))
        except Exception:
            pass
        if result:
            text = f"__Successfully blocked__ {href}"
            if PM_PERMIT and redis and user.id in approvedUsers:
                approvedUsers.remove(user.id)
                await update_db()
                text += " __and remove them from approved users.__"
            await event.answer(text, log=('pmpermit', text))
        else:
            await event.answer(f"__Couldn't block__ {href}")


@client.onMessage(
    command=("unblock", plugin_category),
    outgoing=True, regex=r"unblock(?: |$)(.+)?$"
)
async def unblock(event: NewMessage.Event) -> None:
    """Unblock an user."""
    result = False
    user = await get_user(event)
    if user:
        href = await get_chat_link(user)
        try:
            result = await client(functions.contacts.UnblockRequest(
                id=user.id
            ))
        except Exception:
            pass
        if result:
            text = f"__Successfully unblocked__ {href}"
            await event.answer(text, log=('pmpermit', text))
        else:
            await event.answer(f"__Couldn't unblock__ {href}")


@client.onMessage(
    command=("approved", plugin_category),
    outgoing=True, regex=r"approved$"
)
async def approved(event: NewMessage.Event) -> None:
    """Get a list of all the approved users for PM-Permit."""
    if approvedUsers:
        text = "**Approved users:**\n"
        text += ', '.join([f'`{i}`' for i in approvedUsers])
        await event.answer(text)
    else:
        await event.answer("**You currently have no approved users.**")


async def get_user(event: NewMessage.Event) -> types.User or None:
    match = event.matches[0].group(1)
    user = None
    if match:
        match = int(match) if match.isdigit() else match
        try:
            user = await client.get_entity(match)
        except (TypeError, ValueError):
            await event.answer("`Couldn't fetch the user!`")
            return
    elif event.is_private and event.out:
        user = await event.get_chat()
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user = await reply.get_sender()
    return user


async def update_db() -> None:
    if redis:
        if approvedUsers:
            redis.set('approved:users', dill.dumps(approvedUsers))
        else:
            redis.delete('approved:users')
