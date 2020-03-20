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


from typing import Union

from telethon.tl import types
from telethon.utils import get_peer_id

from ..utils.events import NewMessage


class Parser:
    """Parse UserFull, ChannelFull and ChatFull objects."""

    @staticmethod
    async def parse_full_user(
        usr_obj: types.UserFull,
        event: NewMessage.Event
    ) -> str:
        """Human-friendly string of an User obj's attributes"""
        user = usr_obj.user

        user_id = get_peer_id(user.id)
        is_self = user.is_self
        contact = user.contact
        mutual_contact = user.mutual_contact
        deleted = user.deleted
        is_bot = user.bot
        verified = user.verified
        restricted = user.restricted
        support = user.support
        scam = user.scam
        first_name = user.first_name
        last_name = user.last_name
        username = user.username
        dc_id = user.photo.dc_id if user.photo else None
        common_chats_count = usr_obj.common_chats_count
        blocked = usr_obj.blocked
        about = usr_obj.about
        total_pics = (await event.client.get_profile_photos(user_id)).total

        text = ""  # "**USER**\n"
        text += f"  **ID:** [{user_id}](tg://user?id={user_id})"
        if first_name:
            text += f"\n  **First name:** `{first_name}`"
        if last_name:
            text += f"\n  **Last name:** `{last_name}`"
        if about:
            text += f"\n  **Bio:** `{about}`"
        if username:
            text += f"\n  **Username:** @{username}"
        if common_chats_count:
            text += f"\n  **Groups in common:** `{common_chats_count}`"
        if dc_id:
            text += f"\n  **DC ID:** `{dc_id}`"
        if is_self:
            text += f"\n  **Self:** `{is_self}`"
        if contact:
            text += f"\n  **Contact:** `{contact}`"
        if mutual_contact:
            text += f"\n  **Mutual contact:** `{mutual_contact}`"
        if deleted:
            text += f"\n  **Deleted:** `{deleted}`"
        if is_bot:
            text += f"\n  **Bot:** `{is_bot}`"
        if verified:
            text += f"\n  **Verified:** `{verified}`"
        if support:
            text += f"\n  **TG support team:** `{support}`"
        if restricted:
            text += f"\n  **Restricted for:** `{user.restriction_reason}`"
        if blocked:
            text += f"\n  **Blocked:** `{blocked}`"
        if scam:
            text += f"\n  **Scam:** `{scam}`"
        if total_pics:
            text += f"\n  **Total profile pictures:** `{total_pics}`"
        return text

    @staticmethod
    async def parse_full_chat(
        chat_obj: Union[types.ChatFull, types.ChannelFull],
        event: NewMessage.Event
    ) -> str:
        """Human-friendly string of a Chat/Channel obj's attributes"""
        full_chat = chat_obj.full_chat
        chats = chat_obj.chats[0]
        profile_pic = full_chat.chat_photo

        if isinstance(full_chat, types.ChatFull):
            obj_type = "CHAT"
            participants = len(chats.participants)
        else:
            obj_type = "CHANNEL"
            participants = full_chat.participants_count
            broadcast = chats.broadcast
            megagroup = chats.megagroup
            verified = chats.verified
            admins = full_chat.admins_count
            kicked = full_chat.kicked_count
            banned = full_chat.banned_count
            online = full_chat.online_count

        chat_id = get_peer_id(full_chat.id)
        title = chats.title
        creator = chats.creator
        left = chats.left
        username = chats.username
        dc_id = profile_pic.dc_id if hasattr(profile_pic, "dc_id") else None
        about = full_chat.about
        bots = len(full_chat.bot_info)
        total_pics = (await event.client.get_profile_photos(chat_id)).total

        text = ""  # f"**{obj_type}**\n"
        if username:
            text += f"  **ID:** [{chat_id}](tg://resolve?domain={username})"
        else:
            text += f"  **ID:** `{chat_id}`"
        if title:
            text += f"\n  **Title:** `{title}`"
        if about:
            text += f"\n  **About:** `{about}`"
        if username:
            text += f"\n  **Username:** @{username}"
        if participants:
            text += f"\n  **Total participants:** `{participants}`"
        if creator:
            text += f"\n  **Creator:** `{creator}`"
        if left:
            text += f"\n  **Left:** `{left}`"
        if dc_id:
            text += f"\n  **DC ID:** `{dc_id}`"
        if bots:
            text += f"\n  **Total bots:** `{bots}`"

        if obj_type == "CHANNEL":
            if admins:
                text += f"\n  **Admins:** `{admins}`"
            if kicked:
                text += f"\n  **Kicked:** `{kicked}`"
            if banned:
                text += f"\n  **Banned:** `{banned}`"
            if online:
                text += f"\n  **Online:** `{online}`"
            if broadcast:
                text += f"\n  **Broadcast:** `{broadcast}`"
            if megagroup:
                text += f"\n  **Megagroup:** `{megagroup}`"
            if verified:
                text += f"\n  **Verified:** `{verified}`"

        if total_pics:
            text += f"\n  **Total profile pictures:** `{total_pics}`"
        return text
