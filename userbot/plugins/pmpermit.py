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
from typing import Dict, List

from telethon.tl import functions, types

from userbot import client
from userbot.utils.helpers import get_chat_link
from userbot.utils.events import NewMessage


plugin_category = "pmpermit"
PM_PERMIT = client.config['userbot'].getboolean('pm_permit', False)
redis = client.database

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
    "`You have only` **1** `message left, if you send the next one "
    "you will be blocked and reported!`"
)
default = (
    "`This is an automated message, kindly wait until you're approved.`\n"
    "`Messages remaining:` **{remaining}**"
)
samedefault = "`Messages Remaining:` **{remaining}**"
newdefault = (
    "**This is an automated message, kindly wait until you've been approved "
    "otherwise you'll be blocked and reported for spamming.**\n\n"
    "`Messages Remaining:` **{remaining}**"
)
esc_default = (
    re.escape(default.format(remaining=r'\d')).replace(r'\\d', r'\d')
)
esc_samedefault = (
    re.escape(samedefault.format(remaining=r'\d')).replace(r'\\d', r'\d')
)
esc_newdefault = (
    re.escape(newdefault.format(remaining=r'\d')).replace(r'\\d', r'\d')
)
blocked = "`You've been blocked and reported for spamming.`"
blocklog = (
    "{} `has been blocked for spamming, unblock them to see their messages.`"
)
autoapprove = "`Successfully auto-approved` {user}"

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

    if (
        entity.verified or entity.support or entity.bot or
        sender in approvedUsers
    ):
        return
    elif entity.mutual_contact:
        if sender not in approvedUsers:
            approvedUsers.append(sender)
            await update_db()
            user = await get_chat_link(entity)
            text = autoapprove.format(user=user)
            text += " `for being a mutual contact.`"
            await event.answer(
                text, reply=True,
                self_destruct=2, log=('pmpermit', text)
            )
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
        await event.resanswer(
            blocked, plugin='pmpermit', name='blocked',
            log=('pmpermit', blocklog.format(user))
        )
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
        out = await event.resanswer(
            newdefault, plugin='pmpermit', name='newdefault',
            fromats={'remaining': count}
        )
    else:
        if count == 1:
            out = await event.resanswer(
                warning, plugin='pmpermit', name='warning'
            )
        elif (
            event.text in [PP_UNAPPROVED_MSG, FTG_UNAPPROVED_MSG] or
            re.search(esc_newdefault, event.text) or
            re.search(esc_default, event.text) or
            re.search(esc_samedefault, event.text)
        ):
            pass
        elif lastmsg and event.text == lastmsg:
            out = await event.resanswer(
                samedefault, plugin='pmpermit', name='samedefault',
                formats={'remaining': count}
            )
            lastoutmsg = out.id
        else:
            out = await event.resanswer(
                default, plugin='pmpermit', name='default',
                formats={'remaining': count}
            )

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
    if chat.verified or chat.support or chat.bot or chat.is_self:
        return

    result = await client.get_messages(
        await event.get_input_chat(), reverse=True, limit=1
    )
    if result[0].out:
        if chat.id not in approvedUsers:
            approvedUsers.append(chat.id)
            await update_db()
            user = await get_chat_link(chat)
            await event.resanswer(
                autoapprove, plugin='pmpermit', name='autoapprove',
                formats={'user': user}, reply=True, self_destruct=2,
                log=('pmpermit', autoapprove.format(user=user))
            )


@client.onMessage(
    command=("approve", plugin_category),
    outgoing=True, regex=r"approve(?: |$)(.+)?$"
)
async def approve(event: NewMessage.Event) -> None:
    """
    Approve an user for PM-Permit.


    **{prefix}approve [user1] .. [user n]** in reply to a user/chat
    """
    if not PM_PERMIT or not redis:
        await event.answer("PM-Permit is disabled.")
        return
    users = await get_users(event)
    approved = []
    skipped = []
    if users:
        for user in users:
            href = await get_chat_link(user)
            if user.verified or user.support or user.bot:
                skipped.append(href)
                continue

            if user.id in approvedUsers:
                skipped.append(href)
            else:
                approvedUsers.append(user.id)
                await update_db()
                approved.append(href)
            if user.id in spammers:
                _, _, sent, _ = spammers.pop(user.id)  # Reset the counter
                await client.delete_messages(user, sent)
                await client(functions.account.UpdateNotifySettingsRequest(
                    peer=user.id,
                    settings=DEFAULT_UNMUTE_SETTINGS
                ))
    if approved:
        text = "**Successfully approved:** " + ', '.join(approved)
        await event.answer(text, log=('pmpermit', text))
    if skipped:
        text = "**Skipped users:** " + ', '.join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("unapprove", plugin_category),
    outgoing=True, regex=r"(?:un|dis)approve(?: |$)(.+)?$"
)
async def disapprove(event: NewMessage.Event) -> None:
    """
    Disapprove an user for PM-Permit.


    **{prefix}unapprove [user1] .. [user n]** in reply to a user/chat
    """
    if not PM_PERMIT or not redis:
        await event.answer("PM-Permit is disabled.")
        return
    users = await get_users(event)
    disapproved = []
    skipped = []
    if users:
        for user in users:
            href = await get_chat_link(user)
            if user.id in approvedUsers:
                approvedUsers.remove(user.id)
                await update_db()
                disapproved.append(href)
            else:
                skipped.append(href)
            spammers.pop(user.id, None)  # Reset the counter
    if disapproved:
        text = "**Successfully disapproved:** " + ', '.join(disapproved)
        await event.answer(text, log=('pmpermit', text))
    if skipped:
        text = "**Skipped users:** " + ', '.join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("block", plugin_category),
    outgoing=True, regex=r"block(?: |$)(.+)?$"
)
async def block(event: NewMessage.Event) -> None:
    """
    Block an user and remove them from approved users.


    **{prefix}block [user1] .. [user n]** in reply to a user/chat
    """
    users = await get_users(event)
    blocked = []
    skipped = []
    if users:
        for user in users:
            result = None
            href = await get_chat_link(user)
            try:
                result = await client(functions.contacts.BlockRequest(
                    id=user.id
                ))
            except Exception:
                pass
            if result:
                if PM_PERMIT and redis and user.id in approvedUsers:
                    approvedUsers.remove(user.id)
                    await update_db()
                    href += " and unapproved."
                blocked.append(href)
            else:
                skipped.append(href)
    if blocked:
        text = "**Successfully blocked:** " + ', '.join(blocked)
        await event.answer(text, log=('pmpermit', text))
    if skipped:
        text = "**Skipped users:** " + ', '.join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("unblock", plugin_category),
    outgoing=True, regex=r"unblock(?: |$)(.+)?$"
)
async def unblock(event: NewMessage.Event) -> None:
    """
    Unblock an user.


    **{prefix}unblock [user1] .. [user n]** in reply to a user/chat
    """
    users = await get_users(event)
    unblocked = []
    skipped = []
    if users:
        for user in users:
            result = None
            href = await get_chat_link(user)
            try:
                result = await client(functions.contacts.UnblockRequest(
                    id=user.id
                ))
            except Exception:
                pass
            if result:
                unblocked.append(href)
            else:
                skipped.append(href)
    if unblocked:
        text = "**Successfully unblocked:** " + ', '.join(unblocked)
        await event.answer(text, log=('pmpermit', text))
    if skipped:
        text = "**Skipped users:** " + ', '.join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("approved", plugin_category),
    outgoing=True, regex=r"approved$"
)
async def approved(event: NewMessage.Event) -> None:
    """
    Get a list of all the approved users for PM-Permit.


    `{prefix}approved`
    """
    if approvedUsers:
        text = "**Approved users:**\n"
        text += ', '.join([f'`{i}`' for i in approvedUsers])
        await event.answer(text)
    else:
        await event.answer("`You haven't approved anyone yet.`")


async def get_users(event: NewMessage.Event) -> types.User or None:
    match = event.matches[0].group(1)
    users = []
    if match:
        matches, _ = await client.parse_arguments(match)
        for match in matches:
            try:
                entity = await client.get_entity(match)
                if isinstance(entity, types.User):
                    users.append(entity)
            except (TypeError, ValueError):
                pass
    elif event.is_private and event.out:
        users = [await event.get_chat()]
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        users = [await reply.get_sender()]
    return users


async def update_db() -> None:
    if redis:
        if approvedUsers:
            redis.set('approved:users', dill.dumps(approvedUsers))
        else:
            redis.delete('approved:users')
