# TG-UserBot - A modular Telegram UserBot for Python3.6+. 
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


async def parse_full_user(full_user_object):
    user = full_user_object.user
    profile_pic = full_user_object.profile_photo

    user_id = user.id
    is_self = user.is_self
    contact = user.contact
    mutual_contact = user.mutual_contact
    deleted = user.deleted
    is_bot = user.bot
    verified = user.verified
    restricted = user.restricted
    first_name = user.first_name
    last_name = user.last_name
    username = user.username
    dc_id = user.photo.dc_id if user.photo else None
    common_chats_count = full_user_object.common_chats_count
    blocked = full_user_object.blocked
    about = full_user_object.about

    text = f"__Who is__ {first_name}__?__\n"
    if user_id:
        text += f"\n**ID:** `{user_id}`"
    if username:
        text += f"\n**Username:** `{username}`"
    if first_name:
        text += f"\n**First name:** `{first_name}`"
    if last_name:
        text += f"\n**Last name:** `{last_name}`"
    if about:
        text += f"\n**Bio:** `{about}`"
    if dc_id:
        text += f"\n**DC ID:** `{dc_id}`"
    if common_chats_count:
        text += f"\n**Groups in common:** `{common_chats_count}`"
    if is_self:
        text += f"\n**Self:** `{is_self}`"
    if contact:
        text += f"\n**Contact:** `{contact}`"
    if mutual_contact:
        text += f"\n**Mutual contact:** `{mutual_contact}`"
    if deleted:
        text += f"\n**Deleted:** `{deleted}`"
    if is_bot:
        text += f"\n**Bot:** `{is_bot}`"
    if verified:
        text += f"\n**Verified:** `{verified}`"
    if restricted:
        text += f"\n**Restricted:** `{restricted}`"
    if blocked:
        text += f"\n**Blocked:** `{blocked}`"

    return profile_pic, text