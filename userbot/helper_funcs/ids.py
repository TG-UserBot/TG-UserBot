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


import re
import logging
from typing import Tuple, Union

from telethon.tl import types

from ..utils.events import NewMessage


LOGGER = logging.getLogger(__name__)


async def get_user_from_msg(event: NewMessage.Event) -> Union[int, str, None]:
    """Get a user's ID or username from the event's regex pattern match"""
    user = None
    match = event.matches[0].group(1)

    if match == "this":
        match = str(event.chat.id)

    if event.entities:
        for entity in event.entities:
            if isinstance(entity, types.MessageEntityMentionName):
                return entity.user_id
            elif isinstance(entity, types.MessageEntityMention):
                offset = entity.offset
                length = entity.length
                maxlen = offset + length
                return event.text[offset:maxlen]

    if match:
        if isinstance(match, str) and match.isdigit():
            user = int(match.strip())
        else:
            user = match.strip()

    return user


async def get_entity_from_msg(event: NewMessage.Event) -> Tuple[
    Union[None, types.User], Union[None, bool, str], Union[None, bool, str]
]:
    """Get a User entity and/or a reason from the event's regex pattern"""
    exception = False
    entity = None
    match = event.matches[0].group(1)

    # TODO: Find better logic to differentiate user and reason
    pattern = re.compile(r"(@?\w+|\d+)(?: |$)(.*)")
    user = pattern.match(match).group(1) if match else None
    extra = pattern.match(match).group(2) if match else None
    reply = await event.get_reply_message()

    if reply and not (user and extra):
        user = reply.from_id
        extra = match.strip()

    user = int(user) if isinstance(user, str) and user.isdigit() else user
    if not user:
        return None, None, "Couldn't fetch an entity from your message!"

    try:
        entity = await event.client.get_entity(user)
    except Exception as e:
        exception = True
        LOGGER.exception(e)

    return entity, extra, exception
