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

from userbot import client, LOGGER
from userbot.helper_funcs.ids import get_entity_from_msg
from userbot.helper_funcs.time import split_extra_string
from userbot.utils.helpers import _humanfriendly_seconds, get_chat_link
from userbot.utils.events import NewMessage


plugin_category = "admin"


@client.onMessage(
    command=("promote", plugin_category),
    outgoing=True, regex=r"promote(?: |$)(.*)$", require_admin=True
)
async def promote(event: NewMessage.Event) -> None:
    """Promote a user in a group or channel."""
    if not event.is_private and not await get_rights(event, add_admins=True):
        await event.answer("`You do not have rights to add admins in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't promote users in private chats.`")
        return

    user, extra, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`Promote machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        await client.edit_admin(
            entity=entity,
            user=user,
            is_admin=True,
            title=extra
        )
        text = "`Successfully promoted `{}` (``{}``)!`"
        if extra:
            text += f"\n`Title:` `{extra}`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully promoted {e1} in {e2}"
        if extra:
            log_msg += f"\nTitle: {extra}"

        await event.answer(
            text.format(e1, user.id),
            log=("promote", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("demote", plugin_category),
    outgoing=True, regex=r"demote(?: |$)(.*)$", require_admin=True
)
async def demote(event: NewMessage.Event) -> None:
    """Demote a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer(
            "`You do not have rights to remove admins in here!`"
        )
        return
    elif event.is_private:
        await event.answer("`You can't demote users in private chats.`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`Demote machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        await client.edit_admin(
            entity=entity,
            user=user,
            is_admin=False
        )
        text = "`Successfully demoted `{}` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully demoted {e1} in {e2}"
        if reason:
            log_msg += f"\nReason: {reason}"

        await event.answer(
            text.format(e1, user.id),
            log=("demote", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("ban", plugin_category),
    outgoing=True, regex=r"ban(?: |$)(.*)$", require_admin=True
)
async def ban(event: NewMessage.Event) -> None:
    """Ban a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't ban users in private chats.`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`Ban machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        await client.edit_permissions(
            entity=entity,
            user=user,
            view_messages=False
        )
        text = "`Successfully banned `{}` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully banned {e1} in {e2}"
        if reason:
            log_msg += f"\nReason: {reason}"

        await event.answer(
            text.format(e1, user.id),
            log=("ban", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("unban", plugin_category),
    outgoing=True, regex=r"unban(?: |$)(.*)$", require_admin=True
)
async def unban(event: NewMessage.Event) -> None:
    """Un-ban a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to un-ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't un-ban users in private chats.`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`Un-ban machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
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
        text = "`Successfully un-banned `{}` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully unbanned {e1} in {e2}"
        if reason:
            log_msg += f"\nReason: {reason}"

        await event.answer(
            text.format(e1, user.id),
            log=("unban", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("kick", plugin_category),
    outgoing=True, regex=r"kick(?: |$)(.*)$", require_admin=True
)
async def kick(event: NewMessage.Event) -> None:
    """Kick a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to kick users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't kick users in private chats.`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`Kick machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        await client.kick_participant(
            entity=entity,
            user=user
        )
        text = "`Successfully kicked `{}` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully kicked {e1} in {e2}"
        if reason:
            log_msg += f"\nReason: {reason}"

        await event.answer(
            text.format(e1, user.id),
            log=("kick", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("mute", plugin_category),
    outgoing=True, regex=r"mute(?: |$)(.*)$", require_admin=True
)
async def mute(event: NewMessage.Event) -> None:
    """Mute a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to mute users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't mute users in private chats.`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`Mute machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        await client.edit_permissions(
            entity=entity,
            user=user,
            send_messages=False
        )
        text = "`Successfully muted `{}` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully muted {e1} in {e2}"
        if reason:
            log_msg += f"\nReason: {reason}"

        await event.answer(
            text.format(e1, user.id),
            log=("mute", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("unmute", plugin_category),
    outgoing=True, regex=r"unmute(?: |$)(.*)$", require_admin=True
)
async def unmute(event: NewMessage.Event) -> None:
    """Un-mute a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer(
            "`You do not have rights to un-mute users in here!`"
        )
        return
    elif event.is_private:
        await event.answer("`You can't un-mute users in private chats.`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`Un-mute machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        await client.edit_permissions(
            entity=entity,
            user=user,
            send_messages=True
        )
        text = "`Successfully un-muted `{}` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully un-muted {e1} in {e2}"
        if reason:
            log_msg += f"\nReason: {reason}"

        await event.answer(
            text.format(e1, user.id),
            log=("unmute", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("tmute", plugin_category),
    outgoing=True, regex=r"tmute(?: |$)(.*)$", require_admin=True
)
async def tmute(event: NewMessage.Event) -> None:
    """Temporary mute a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to mute users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't t-mute users in private chats.`")
        return

    user, extra, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`T-mute machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        time = None
        reason = None
        seconds = None
        text = "`Successfully t-muted `{}` (``{}``)!`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully tmuted {e1} in {e2}"
        if extra:
            reason, seconds = await split_extra_string(extra)
            if reason:
                text += f"\n`Reason:` `{reason}`"
                log_msg += f"\nReason: {reason}"
            if seconds:
                time = timedelta(seconds=seconds)
                text += f"\n`Time:` `{await _humanfriendly_seconds(seconds)}`"
                log_msg += f"\nTime: {await _humanfriendly_seconds(seconds)}"

        if not seconds:
            await event.answer("`Provide the total time limit for t-mute!`")
            return

        await client.edit_permissions(
            entity=entity,
            user=user,
            until_date=time,
            send_messages=False
        )

        await event.answer(
            text.format(e1, user.id),
            log=("tmute", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command=("tban", plugin_category),
    outgoing=True, regex=r"tban(?: |$)(.*)$", require_admin=True
)
async def tban(event: NewMessage.Event) -> None:
    """Temporary ban a user in a group or channel."""
    if not event.is_private and not await get_rights(event, ban_users=True):
        await event.answer("`You do not have rights to t-ban users in here!`")
        return
    elif event.is_private:
        await event.answer("`You can't t-ban users in private chats.`")
        return

    user, extra, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.answer(f"`T-ban machine broke!\n{user}`")
            return
    else:
        await event.answer("`At least specifiy a user, maybe?`")
        return

    entity = await event.get_chat()
    try:
        time = None
        reason = None
        seconds = None
        text = "`Successfully t-banned `{}` (``{}``)!`"
        e1 = await get_chat_link(user)
        e2 = await get_chat_link(entity, event.id)
        log_msg = f"Successfully t-banned {e1} in {e2}"
        if extra:
            reason, seconds = await split_extra_string(extra)
            if reason:
                text += f"\n`Reason:` `{reason}`"
                log_msg += f"\nReason: {reason}"
            if seconds:
                time = timedelta(seconds=seconds)
                text += f"\n`Time:` `{await _humanfriendly_seconds(seconds)}`"
                log_msg += f"Time: {await _humanfriendly_seconds(seconds)}"

        if not seconds:
            await event.answer("`Provide the total time limit for t-ban!`")
            return

        await client.edit_permissions(
            entity=entity,
            user=user,
            until_date=time,
            view_messages=False
        )

        await event.answer(
            text.format(e1, user.id),
            log=("tban", log_msg)
        )
    except Exception as e:
        await event.answer(f"`{e}`")
        LOGGER.exception(e)


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
