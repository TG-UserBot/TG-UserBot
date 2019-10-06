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
from logging import getLogger
from typing import Union

from telethon.tl.types import (
    Message, MessageEntityMention, MessageEntityMentionName
)


LOGGER = getLogger()


async def get_user_from_msg(event: Message) -> Union[int, str, None]:
    user = None
    match = event.matches[0].group(1)

    if match == "this":
        match = event.chat_id

    if event.entities:
        for entity in event.entities:
            if isinstance(entity, MessageEntityMentionName):
                return entity.user_id
            elif isinstance(entity, MessageEntityMention):
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


async def get_entity_from_msg(event: Message) -> Union[int, str, None]:
    exception = False
    entity = None
    match = event.matches[0].group(1)

    pattern = re.compile(r"(@\w*|\w*|\d*)(?: |$)(.*)")
    user = pattern.match(match).group(1)
    extra = pattern.match(match).group(2)
    reply = await event.get_reply_message()

    if reply and user:
        extra = user + extra
        user = str(reply.from_id)

    user = int(user) if user.isdigit() else str(user)

    try:
        entity = await event.client.get_entity(user)
    except Exception as e:
        exception = True
        entity = e
        LOGGER.exception(e)

    return entity, extra, exception
