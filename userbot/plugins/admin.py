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


from datetime import timedelta

from userbot import client
from userbot.helper_funcs.time import string_to_secs
from userbot.utils.helpers import _humanfriendly_seconds, get_chat_link
from userbot.utils.events import NewMessage


plugin_category = "admin"


@client.onMessage(
    command=("promote", plugin_category),
    outgoing=True, regex=r"promote(?: |$|\n)([\s\S]*)", require_admin=True
)
async def promote(event: NewMessage.Event) -> None:
    """
    Promote a user in a group or channel.


    `{prefix}promote` in reply or **{prefix}promote user1 user2 [kwargs]**
        **Arguments:** `reason` and `title`
    """
    if not event.is_private and not await get_rights(event, add_admins=True):
        await event.answer("`You do not have rights to add admins in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't promote users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    title = kwargs.get('title', None)
    skipped = []
    promoted = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_admin(
                entity=entity,
                user=user,
                is_admin=True,
                title=title
            )
            promoted.append(user)
        except Exception:
            skipped.append(user)
    if promoted:
        text = f"`Successfully promoted:`\n"
        text += ', '.join((f'`{x}`' for x in promoted))
        if title:
            text += f"\n`Title:` `{title}`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("promote", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("demote", plugin_category),
    outgoing=True, regex=r"demote(?: |$|\n)([\s\S]*)", require_admin=True
)
async def demote(event: NewMessage.Event) -> None:
    """
    Demote a user in a group or channel.


    `{prefix}demote` in reply or **{prefix}demote user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer(
            "`You do not have rights to remove admins in here!`"
        )
        return
    elif event.is_private:
        await event.answer("`You can't demote users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    skipped = []
    demoted = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_admin(
                entity=entity,
                user=user,
                is_admin=False
            )
            demoted.append(user)
        except Exception:
            skipped.append(user)
    if demoted:
        text = f"`Successfully demoted:`\n"
        text += ', '.join((f'`{x}`' for x in demoted))
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("demote", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("ban", plugin_category),
    outgoing=True, regex=r"ban(?: |$|\n)([\s\S]*)", require_admin=True
)
async def ban(event: NewMessage.Event) -> None:
    """
    Ban a user in a group or channel.


    `{prefix}ban` in reply or **{prefix}ban user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't ban users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    skipped = []
    banned = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                view_messages=False
            )
            banned.append(user)
        except Exception:
            skipped.append(user)
    if banned:
        text = f"`Successfully banned:`\n"
        text += ', '.join((f'`{x}`' for x in banned))
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("ban", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("unban", plugin_category),
    outgoing=True, regex=r"unban(?: |$|\n)([\s\S]*)", require_admin=True
)
async def unban(event: NewMessage.Event) -> None:
    """
    Un-ban a user in a group or channel.


    `{prefix}unban` in reply or **{prefix}unban user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to un-ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't un-ban users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    skipped = []
    unbanned = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                view_messages=True,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                send_polls=True
            )
            unbanned.append(user)
        except Exception:
            skipped.append(user)
    if unbanned:
        text = f"`Successfully unbanned:`\n"
        text += ', '.join((f'`{x}`' for x in unbanned))
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("unban", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("kick", plugin_category),
    outgoing=True, regex=r"kick(?: |$|\n)([\s\S]*)", require_admin=True
)
async def kick(event: NewMessage.Event) -> None:
    """
    Kick a user in a group or channel.


    `{prefix}kick` in reply or **{prefix}kick user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to kick users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't kick users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    skipped = []
    kicked = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.kick_participant(
                entity=entity,
                user=user
            )
            kicked.append(user)
        except Exception:
            skipped.append(user)
    if kicked:
        text = f"`Successfully kicked:`\n"
        text += ', '.join((f'`{x}`' for x in kicked))
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("kick", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("mute", plugin_category),
    outgoing=True, regex=r"mute(?: |$|\n)([\s\S]*)", require_admin=True
)
async def mute(event: NewMessage.Event) -> None:
    """
    Mute a user in a group or channel.


    `{prefix}mute` in reply or **{prefix}mute user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to mute users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't mute users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    skipped = []
    muted = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                send_messages=False
            )
            muted.append(user)
        except Exception:
            skipped.append(user)
    if muted:
        text = f"`Successfully muted:`\n"
        text += ', '.join((f'`{x}`' for x in muted))
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("mute", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("unmute", plugin_category),
    outgoing=True, regex=r"unmute(?: |$|\n)([\s\S]*)", require_admin=True
)
async def unmute(event: NewMessage.Event) -> None:
    """
    Un-mute a user in a group or channel.


    `{prefix}unmute` in reply or **{prefix}unmute user1 user2 [kwargs]**
        **Arguments:** `reason`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer(
            "`You do not have rights to un-mute users in here!`"
        )
        return
    elif event.is_private:
        await event.answer("`You can't un-mute users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    skipped = []
    unmuted = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                send_messages=True
            )
            unmuted.append(user)
        except Exception:
            skipped.append(user)
    if unmuted:
        text = f"`Successfully unmuted:`\n"
        text += ', '.join((f'`{x}`' for x in unmuted))
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("unmute", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("tmute", plugin_category),
    outgoing=True, regex=r"tmute(?: |$|\n)([\s\S]*)", require_admin=True
)
async def tmute(event: NewMessage.Event) -> None:
    """
    Temporary mute a user in a group or channel.


    `{prefix}tmute` in reply or **{prefix}tmute user1 user2 [kwargs]**
        **Arguments:** `reason` and `time`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to mute users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't t-mute users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    period = kwargs.get('time', None)
    if not period:
        await event.answer("`Specify the time by using time=<n>`")
        return
    period = await string_to_secs(period)
    skipped = []
    unmuted = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                until_date=timedelta(seconds=period),
                send_messages=False
            )
            unmuted.append(user)
        except Exception:
            skipped.append(user)
    if unmuted:
        text = f"`Successfully tmuted:`\n"
        text += ', '.join((f'`{x}`' for x in unmuted))
        text += f"\n`Time:` `{await _humanfriendly_seconds(period)}`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("tmute", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)


@client.onMessage(
    command=("tban", plugin_category),
    outgoing=True, regex=r"tban(?: |$|\n)([\s\S]*)", require_admin=True
)
async def tban(event: NewMessage.Event) -> None:
    """
    Temporary ban a user in a group or channel.


    `{prefix}tban` in reply or **{prefix}tban user1 user2 [kwargs]**
        **Arguments:** `reason` and `time`
    """
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to t-ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't t-ban users in private chats.`")
        return

    match = event.matches[0].group(1)
    args, kwargs = await client.parse_arguments(match)
    reason = kwargs.get('reason', None)
    period = kwargs.get('time', None)
    if not period:
        await event.answer("`Specify the time by using time=<n>`")
        return
    period = await string_to_secs(period)
    skipped = []
    banned = []

    if not args and event.reply_to_msg_id:
        reply = await event.get_reply_message()
        args.append(reply.sender_id)
    if not args:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    for user in args:
        if isinstance(user, list):
            continue
        try:
            await client.edit_permissions(
                entity=entity,
                user=user,
                until_date=timedelta(seconds=period),
                view_messages=False
            )
            banned.append(user)
        except Exception:
            skipped.append(user)
    if banned:
        text = f"`Successfully tbanned:`\n"
        text += ', '.join((f'`{x}`' for x in banned))
        text += f"\n`Time:` `{await _humanfriendly_seconds(period)}`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e2 = await get_chat_link(entity, event.id)
        log_msg = text + f"\n`Chat:` {e2}"
        await event.answer(text, log=("tban", log_msg))
    if skipped:
        text = "`Skipped users:`"
        text += ', '.join((f'`{x}`' for x in skipped))
        await event.answer(text, reply=True)

@client.onMessage(command=("pin", plugin_category), outgoing=True, regex=r"(loud)?pin$", require_admin=True)
async def pin(event: NewMessage.Event) -> None:
    """Pin the message at the top of the group or channel."""
    if not event.is_private and not await get_rights(event, pin_messages=True):
        await event.answer("`You do not have rights to pin messages in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't pin messages in private chats.`")
        return

    notify = bool(event.matches[0].group(1))

    if not event.reply_to_msg_id:
        await event.answer("`Pinned the void.`")
        return

    entity = await event.get_chat()
    try:
        await client.pin_message(entity=entity, message=event.reply_to_msg_id, notify=notify)
        text = "`Successfully pinned!`\n"
        text += f"`Loud-Pin:` `{'Yes' if notify else 'No'}`\n"
    except Exception:
        text = "`Failed to pin the message!`\n"
    e2 = await get_chat_link(event, event.reply_to_msg_id)
    log_msg = text + f"\n`Chat:` {e2}"
    await event.answer(text, log=("pin", log_msg))

async def get_rights(
    event: NewMessage.Event,
    change_info: bool = False,
    post_messages: bool = False,
    edit_messages: bool = False,
    delete_messages: bool = False,
    ban_users: bool = False,
    invite_users: bool = False,
    pin_messages: bool = False,
    add_admins: bool = False
) -> bool:
    """Return a bool according the required rights"""
    chat = await event.get_chat()
    if chat.creator:
        return True
    rights = {
        'change_info': change_info,
        'post_messages': post_messages,
        'edit_messages': edit_messages,
        'delete_messages': delete_messages,
        'ban_users': ban_users,
        'invite_users': invite_users,
        'pin_messages': pin_messages,
        'add_admins': add_admins
    }
    required_rights = []
    for right, required in rights.items():
        if required:
            required_rights.append(getattr(chat.admin_rights, right, False))

    return all(required_rights)
