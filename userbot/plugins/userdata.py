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


from io import BytesIO
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.functions.account import (
    UpdateProfileRequest, UpdateUsernameRequest
)
from telethon.tl.functions.photos import (
    DeletePhotosRequest, UploadProfilePhotoRequest
)
from telethon.tl.types import (
    InputPeerChat, InputPeerChannel, MessageMediaPhoto, MessageMediaDocument
)
from telethon.errors import (
    AboutTooLongError, FirstNameInvalidError, UsernameInvalidError,
    UsernameNotModifiedError, UsernameOccupiedError, FilePartsInvalidError,
    ImageProcessFailedError, PhotoCropSizeSmallError, PhotoExtInvalidError
)

from userbot import client
from userbot.helper_funcs.ids import get_user_from_msg
from userbot.helper_funcs.parser import Parser


@client.onMessage(
    command="whois", info="Get information about a user or chat",
    outgoing=True, regex=r"(?:who|what)is(?: |$)(.*)$"
)
async def whois(event):
    match = event.matches[0].group(1)
    reply_id = None

    if event.entities or match:
        user = await get_user_from_msg(event)
        if not user:
            await event.edit("`Couldn't get user/chat from the message.`")
            return
    else:
        user = "self"

    if event.reply_to_msg_id:
        reply_id = event.reply_to_msg_id
        if not match:
            reply = await event.get_reply_message()
            if reply.fwd_from:
                if reply.fwd_from.from_id:
                    user = reply.fwd_from.from_id
                else:
                    user = reply.sender_id

    try:
        input_entity = await client.get_input_entity(user)
    except Exception as e:
        await event.reply('`' + type(e).__name__ + ': ' + str(e) + '`')
        return

    try:
        if isinstance(input_entity, InputPeerChat):
            full_chat = await client(
                GetFullChatRequest(chat_id=input_entity)
            )
            string = await Parser.parse_full_chat(full_chat, event)
        elif isinstance(input_entity, InputPeerChannel):
            full_channel = await client(
                GetFullChannelRequest(channel=input_entity)
            )
            string = await Parser.parse_full_chat(full_channel, event)
        else:
            full_user = await client(
                GetFullUserRequest(id=input_entity)
            )
            string = await Parser.parse_full_user(full_user, event)
    except Exception as e:
        await event.reply('`' + type(e).__name__ + ': ' + str(e) + '`')
        return

    if reply_id:
        await event.delete()
    await event.respond(string, reply_to=reply_id)


@client.onMessage(
    command="name", info="Change your name",
    outgoing=True, regex="name(?: |$)(.*)$"
)
async def name(event):
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
        await client(UpdateProfileRequest(
            first_name=first,
            last_name=last
        ))
        await event.edit("`Name was successfully changed.`")
    except FirstNameInvalidError:
        await event.edit("`The first name is invalid.`")
    except Exception as e:
        await event.reply('`' + type(e).__name__ + ': ' + str(e) + '`')


@client.onMessage(
    command="bio", info="Change your bio",
    outgoing=True, regex="bio(?: |$)(.*)$"
)
async def bio(event):
    match = event.matches[0].group(1)
    if not match:
        about = (await client(GetFullUserRequest("self"))).about
        if about:
            await event.edit(f"**{about}**")
        else:
            await event.edit("`You currently have no bio.`")
        return

    try:
        await client(UpdateProfileRequest(about=match))
        await event.edit("`Bio was successfully changed.`")
    except AboutTooLongError:
        await event.edit("`The about text is too long.`")


@client.onMessage(
    command="username", info="Change your username",
    outgoing=True, regex="username(?: |$)(.*)$"
)
async def username(event):
    match = event.matches[0].group(1)
    if not match:
        username = (await client.get_me()).username
        if username:
            await event.edit(f"**{username}**")
        else:
            await event.edit("`You currently have no username.`")
        return

    try:
        await client(UpdateUsernameRequest(username=match))
        await event.edit(f"`Successfully changed username to {match}`")
    except UsernameOccupiedError:
        await event.edit("`The username is already in use.`")
    except UsernameNotModifiedError:
        await event.edit("`The username was not modified.`")
    except UsernameInvalidError:
        await event.edit("`The username is invalid.`")


@client.onMessage(
    command="pfp", info="Change your username",
    outgoing=True, regex="pfp$"
)
async def pfp(event):
    reply = await event.get_reply_message()
    if not reply:
        photo = (await client(GetFullUserRequest("self"))).profile_photo
        if photo:
            await event.delete()
            await event.respond(file=photo)
        else:
            await event.edit("`You currently have no profile picture.`")
        return

    if not reply.media:
        await event.edit(
            "`What do I use to update the profile picture, a text?`"
        )
        return

    allowed = [MessageMediaDocument, MessageMediaPhoto]
    if type(reply.media) in allowed:
        try:
            temp_file = BytesIO()
            await client.download_media(reply, temp_file)
        except Exception as e:
            await event.reply('`' + type(e).__name__ + ': ' + str(e) + '`')
            temp_file.close()
            return
        temp_file.seek(0)
        photo = await client.upload_file(temp_file)
        temp_file.close()
    else:
        await event.edit("`Invalid media type.`")
        return

    try:
        await client(UploadProfilePhotoRequest(photo))
        await event.edit("`Profile photo was successfully changed.`")
    except FilePartsInvalidError:
        await event.edit("`The number of file parts is invalid.`")
    except ImageProcessFailedError:
        await event.edit("`Failure while processing image.`")
    except PhotoCropSizeSmallError:
        await event.edit("`Photo is too small.`")
    except PhotoExtInvalidError:
        await event.edit("`The extension of the photo is invalid.`")


@client.onMessage(
    command="delpfp", info="Delete your profile pictures",
    outgoing=True, regex=r"delpfp(?: |$)(\d*|all)$"
)
async def delpfp(event):
    match = event.matches[0].group(1)
    if not match:
        count = (await client.get_profile_photos("self")).total
        amount = ("one profile picture." if count == 1
                  else f"{count} profile pictures.")
        await event.edit(f"`You currently have {amount.total}`")
        return

    await event.edit("`Processing all the profile pictures...`")
    limit = 0 if match == "all" else int(match)
    photos = await client.get_profile_photos("self", limit)
    count = len(photos)
    await client(DeletePhotosRequest(photos))
    amount = ("current profile picture." if count == 1
              else f"{count} profile pictures.")
    text = f"`Successfully deleted {amount}`"
    await event.edit(text)
