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


from telethon.tl.types import InputPeerUser, InputPeerSelf
from telethon.tl.functions.users import GetFullUserRequest

from userbot import client
from userbot.events import message
from userbot.helper_funcs.ids import get_user_from_entity
from userbot.helper_funcs.parser import parse_full_user


@message(outgoing=True, pattern=r"^.whois(?: |$)(.*)$")
async def whois(event):
    match = event.pattern_match.group(1)
    if event.entities:
        user = await get_user_from_entity(event)
        if not user:
            await event.edit("Couldn't get user from entity.")
            return
    else:
        if match:
            user = int(match) if match.isdigit() else match
        else:
            user = "self"
    
    if event.reply_to_msg_id and not match:
        reply = await event.get_reply_message()
        user = reply.sender_id
    
    try:
        input_entity = await client.get_input_entity(user)
    except Exception as e:
        await event.edit(type(e).__name__ + ': ' + str(e))
        return

    allowed = [InputPeerUser, InputPeerSelf]
    if type(input_entity) not in allowed:
        await event.edit("Specified entity isn't a user.")
        return
    
    full_user = await client(GetFullUserRequest(input_entity))
    pfp, string = await parse_full_user(full_user)
    await event.delete()
    await event.respond(string, file=pfp)