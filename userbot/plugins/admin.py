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
from telethon.utils import get_display_name

from userbot import client, LOGGER
from userbot.helper_funcs.ids import get_entity_from_msg
from userbot.helper_funcs.time import split_extra_string


@client.onMessage(
    command="promote", info="Promote someone in a group|channel.",
    outgoing=True, regex=r"promote(?: |$)(.*)$", require_admin=True
)
async def promote(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.admin_rights.add_admins)
    ):
        await event.edit("`You do not have rights to add admins in here!`")
        return

    user, extra, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`Promote machine broke!\n{user}`")
            return

    try:
        await client.edit_admin(
            entity=await event.get_input_chat(),
            user=user,
            is_admin=True,
            title=extra
        )
        text = "`Successfully promoted ``{}`` (``{}``)!`"
        if extra:
            text += f"\n`Title:` `{extra}`"
        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="demote", info="Demote someone in a group|channel.",
    outgoing=True, regex=r"demote(?: |$)(.*)$", require_admin=True
)
async def demote(event):
    if (
        (event.is_channel or event.is_group) and
        not (
            event.chat.creator or event.chat.admin_rights.ban_users
        )
    ):
        await event.edit("`You do not have rights to remove admins in here!`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`Demote machine broke!\n{user}`")
            return

    try:
        await client.edit_admin(
            entity=await event.get_input_chat(),
            user=user,
            is_admin=False
        )
        text = "`Successfully demoted ``{}`` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="ban", info="Ban someone in a group|channel.",
    outgoing=True, regex=r"ban(?: |$)(.*)$", require_admin=True
)
async def ban(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.admin_rights.ban_users)
    ):
        await event.edit("`You do not have rights to ban users in here!`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`Ban machine broke!\n{user}`")
            return

    try:
        await client.edit_permissions(
            entity=await event.get_input_chat(),
            user=user,
            view_messages=False
        )
        text = "`Successfully banned ``{}`` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="unban", info="Un-ban someone in a group|channel.",
    outgoing=True, regex=r"unban(?: |$)(.*)$", require_admin=True
)
async def unban(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.admin_rights.ban_users)
    ):
        await event.edit("`You do not have rights to un-ban users in here!`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`Un-ban machine broke!\n{user}`")
            return

    try:
        await client.edit_permissions(
            entity=await event.get_input_chat(),
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
        text = "`Successfully un-banned ``{}`` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="kick", info="Kick someone in a group|channel.",
    outgoing=True, regex=r"kick(?: |$)(.*)$", require_admin=True
)
async def kick(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.admin_rights.ban_users)
    ):
        await event.edit("`You do not have rights to kick users in here!`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`Kick machine broke!\n{user}`")
            return

    try:
        await client.kick_participant(
            entity=await event.get_input_chat(),
            user=user
        )
        text = "`Successfully kicked ``{}`` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="mute", info="Mute someone in a group|channel.",
    outgoing=True, regex=r"mute(?: |$)(.*)$", require_admin=True
)
async def mute(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.ban_users)
    ):
        await event.edit("`You do not have rights to mute users in here!`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`Mute machine broke!\n{user}`")
            return

    try:
        await client.edit_permissions(
            entity=await event.get_input_chat(),
            user=user,
            send_messages=False
        )
        text = "`Successfully muted ``{}`` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="unmute", info="Un-mute someone in a group|channel.",
    outgoing=True, regex=r"unmute(?: |$)(.*)$", require_admin=True
)
async def unmute(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.ban_users)
    ):
        await event.edit("`You do not have rights to un-mute users in here!`")
        return

    user, reason, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`Un-mute machine broke!\n{user}`")
            return

    try:
        await client.edit_permissions(
            entity=await event.get_input_chat(),
            user=user,
            send_messages=True
        )
        text = "`Successfully un-muted ``{}`` (``{}``)!`"
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="tmute", info="T-mute someone in a group|channel.",
    outgoing=True, regex=r"tmute(?: |$)(.*)$", require_admin=True
)
async def tmute(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.ban_users)
    ):
        await event.edit("`You do not have rights to mute users in here!`")
        return

    user, extra, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`T-mute machine broke!\n{user}`")
            return

    try:
        time = None
        reason = None
        seconds = None
        text = "`Successfully t-muted ``{}`` (``{}``)!`"
        if extra:
            reason, seconds = await split_extra_string(extra)
            if reason:
                text += f"\n`Reason:` `{reason}`"
            if seconds:
                time = timedelta(seconds=seconds)
                text += f"\n`Time:` `{time}`"

        if not seconds:
            await event.edit("`Provide the total time limit for t-mute!`")
            return

        await client.edit_permissions(
            entity=await event.get_input_chat(),
            user=user,
            until_date=time,
            send_messages=False
        )

        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)


@client.onMessage(
    command="tban", info="T-ban someone in a group|channel.",
    outgoing=True, regex=r"tban(?: |$)(.*)$", require_admin=True
)
async def tban(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.admin_rights.ban_users)
    ):
        await event.edit("`You do not have rights to t-ban users in here!`")
        return

    user, extra, exception = await get_entity_from_msg(event)
    if user:
        if exception:
            await event.edit(f"`T-ban machine broke!\n{user}`")
            return
    try:
        time = None
        reason = None
        seconds = None
        text = "`Successfully t-banned ``{}`` (``{}``)!`"
        if extra:
            reason, seconds = await split_extra_string(extra)
            if reason:
                text += f"\n`Reason:` `{reason}`"
            if seconds:
                time = timedelta(seconds=seconds)
                text += f"\n`Time:` `{time}`"

        if not seconds:
            await event.edit("`Provide the total time limit for t-ban!`")
            return

        await client.edit_permissions(
            entity=await event.get_input_chat(),
            user=user,
            until_date=time,
            view_messages=False
        )

        await event.edit(
            text.format(get_display_name(user), user.id)
        )
    except Exception as e:
        await event.edit(f"`{e}`")
        LOGGER.exception(e)
