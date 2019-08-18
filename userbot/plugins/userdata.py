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


from os import remove
from pyrogram.api.functions.users import GetFullUser
from pyrogram.api.functions.messages import GetFullChat
from pyrogram.api.functions.channels import GetFullChannel
from pyrogram.api.functions.account import UpdateProfile
from pyrogram.api.types import InputPeerChannel, InputPeerChat
from pyrogram.errors import (
    RPCError, UsernameNotOccupied, FirstnameInvalid, LastnameInvalid,
    AboutTooLong, UsernameInvalid, UsernameNotModified, UsernameOccupied,
    PeerIdInvalid
)

from userbot.events import basic_command, commands
from userbot.helper_funcs.ids import get_user_from_msg
from userbot.helper_funcs.parser import Parser


@commands("whois")
@basic_command(command=r"(?:who|what)is(?: |$)(.*)$")
async def whois(client, event):
    match = event.matches[0].group(1)
    reply = event.reply_to_message
    reply_id = None

    if event.entities or match:
        user = await get_user_from_msg(event)
        if not user:
            await event.edit("`Couldn't get user/chat from the message.`")
            return
    else:
        user = "self"

    if reply:
        reply_id = reply.message_id
        if not match:
            if reply.forward_from:
                user = reply.forward_from.id
            else:
                user = reply.from_user.id

    try:
        input_entity = await client.resolve_peer(user)
    except UsernameNotOccupied:
        await event.edit("`This username is not occupied.`")
        return
    except UsernameInvalid:
        await event.edit("`This username is invalid.`")
        return
    except PeerIdInvalid:
        await event.edit("`The id/access_hash combination is invalid.`")
        return
    except KeyError:
        await event.edit("`Peer doesn’t exist in the internal database.`")
        return
    except Exception as E:
        await event.edit(f"`I don't know what the hell happened.`\n\n{E}")
        return

    try:
        if isinstance(input_entity, InputPeerChat):
            full_chat = await client.send(
                GetFullChat(chat_id=input_entity)
            )
            pfp, string = await Parser.parse_full_chat(full_chat)
        elif isinstance(input_entity, InputPeerChannel):
            full_channel = await client.send(
                GetFullChannel(channel=input_entity)
            )
            pfp, string = await Parser.parse_full_chat(full_channel)
        else:
            full_user = await client.send(
                GetFullUser(id=input_entity)
            )
            pfp, string = await Parser.parse_full_user(full_user)
    except RPCError as RCP:
        await event.edit(RCP)
        return

    await event.delete()
    if pfp:
        photo = await client.get_profile_photos(user, limit=1)
        await client.send_photo(
            event.chat.id,
            photo=photo[0].file_id,
            caption=string,
            reply_to_message_id=reply_id
        )
    else:
        await client.send_message(
            event.chat.id,
            string,
            reply_to_message_id=reply_id
        )


@commands("name")
@basic_command(command="name(?: |$)(.*)$")
async def name(client, event):
    match = event.matches[0].group(1)
    if not match:
        me = await client.get_me()
        text = f"**First name:** `{me.first_name}`"
        if me.last_name:
            text += f"\n**Last name:** `{me.last_name}`"
        await event.edit(text)
        return

    split = match.split("last=")
    first = split[0] if split[0] else None
    last = split[1] if len(split) == 2 else None

    try:
        await client.send(UpdateProfile(
            first_name=first,
            last_name=last
        ))
        await event.edit("`Name was successfully changed.`")
    except FirstnameInvalid:
        await event.edit("`The first name is invalid.`")
    except LastnameInvalid:
        await event.edit("`The last name is invalid.`")


@commands("bio")
@basic_command(command="bio(?: |$)(.*)$")
async def bio(client, event):
    match = event.matches[0].group(1)
    if not match:
        entity = await client.resolve_peer("self")
        about = (await client.send(GetFullUser(id=entity))).about
        if about:
            await event.edit(f"**{about}**")
        else:
            await event.edit("`You currently have no bio.`")
        return

    try:
        await client.send(UpdateProfile(about=match))
        await event.edit("`Bio was successfully changed.`")
    except AboutTooLong:
        await event.edit("`The about text is too long.`")


@commands("username")
@basic_command(command="username(?: |$)(.*)$")
async def username(client, event):
    match = event.matches[0].group(1)
    if not match:
        username = event.from_user.username
        if username:
            await event.edit(f"**{username}**")
        else:
            await event.edit("No username found.")
        return

    try:
        await client.update_username(username=match)
    except UsernameOccupied:
        await event.edit("`The username is already in use.`")
    except UsernameNotModified:
        await event.edit("`The username was not modified.`")
    except UsernameInvalid:
        await event.edit("`The username is invalid.`")


@commands("pfp")
@basic_command(command="pfp$")
async def pfp(client, event):
    reply = event.reply_to_message
    if not reply:
        photo = await client.get_profile_photos("self", limit=1)
        if photo:
            pfp = await client.download_media(photo[0])
            await event.delete()
            await client.send_photo(event.chat.id, photo=pfp)
            remove(pfp)
        else:
            await event.edit("`You currently have no profile picture.`")
        return

    if not reply.media:
        await event.edit(
            "`What do I use to update the profile picture, a text?`"
        )
        return

    if reply.photo or reply.document:
        try:
            temp_file = await client.download_media(reply)
            if not temp_file:
                await event.edit("`Couldn't download the media.`")
                return
        except RPCError:
            await event.edit(RPCError)
            return
    else:
        await event.edit("`Invalid media type.`")
        return

    try:
        await client.set_profile_photo(temp_file)
        remove(temp_file)
        await event.edit("`Profile photo was successfully changed.`")
    except RPCError:
        await event.edit(RPCError)


@commands("delpfp")
@basic_command(command=r"delpfp(?: |$)(\d*)$")
async def delpfp(client, event):
    match = event.matches[0].group(1)
    if not match:
        count = await client.get_profile_photos_count("self", None)
        amount = ("one profile picture." if count == 1
                  else f"{count} profile pictures.")
        await event.edit(f"`You currently have {amount}`")
        return

    await event.edit("`Processing all the profile pictures...`")
    limit = None if int(match) == 0 else int(match)
    photos = client.iter_profile_photos(
        chat_id="self",
        limit=limit,
        offset=0
    )
    total_photos = [photo async for photo in photos]
    await client.delete_profile_photos(total_photos)
    amount = ("current profile picture." if len(photos) == 1
              else f"{len(photos)} profile pictures.")
    text = f"`Successfully deleted {amount}`"
    await event.edit(text)
