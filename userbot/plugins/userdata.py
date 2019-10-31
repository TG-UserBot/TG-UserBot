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
from telethon.utils import get_display_name, get_peer_id
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

plugin_category = "user"


@client.onMessage(
    command=("whois", plugin_category),
    outgoing=True, regex=r"(?:who|what)is(?: |$)(.*)$"
)
async def whois(event):
    """Get your or a user's/chat's information."""
    match = event.matches[0].group(1)

    if event.entities or match:
        user = await get_user_from_msg(event)
        if not user:
            await event.answer("`Couldn't get user/chat from the message.`")
            return
    else:
        user = "self"

    if event.reply_to_msg_id:
        if not match:
            reply = await event.get_reply_message()
            if reply.fwd_from:
                if reply.fwd_from.from_id:
                    user = reply.fwd_from.from_id
                else:
                    user = reply.sender_id
            if user == "self":
                user = reply.from_id

    try:
        input_entity = await client.get_input_entity(user)
    except Exception as e:
        await event.answer(
            '`' + type(e).__name__ + ': ' + str(e) + '`',
            reply=True
        )
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
        await event.answer(
            '`' + type(e).__name__ + ': ' + str(e) + '`',
            reply=True
        )
        return

    await event.answer(string)


@client.onMessage(
    command=("name", plugin_category),
    outgoing=True, regex="name(?: |$)(.*)$"
)
async def name(event):
    """Get your current name or update it."""
    match = event.matches[0].group(1)
    if not match:
        me = await client.get_me()
        text = f"**First name:** `{me.first_name}`"
        if me.last_name:
            text += f"\n**Last name:** `{me.last_name}`"
        await event.answer(text)
        return

    split = match.split("last=")
    first = split[0] if split[0] else None
    last = split[1] if len(split) == 2 else None
    n1 = get_display_name(await client.get_me())

    try:
        await client(UpdateProfileRequest(
            first_name=first,
            last_name=last
        ))
        n2 = get_display_name(await client.get_me())
        await event.answer(
            "`Name was successfully changed.`",
            log=("name", f"Name changed from {n1} to {n2}")
        )
    except FirstNameInvalidError:
        await event.answer("`The first name is invalid.`")
    except Exception as e:
        await event.answer('`' + type(e).__name__ + ': ' + str(e) + '`')


@client.onMessage(
    command=("bio", plugin_category),
    outgoing=True, regex="bio(?: |$)(.*)$"
)
async def bio(event):
    """Get your current bio or update it."""
    match = event.matches[0].group(1)
    about = (await client(GetFullUserRequest("self"))).about
    if not match:
        if about:
            await event.answer(f"**{about}**")
        else:
            await event.answer("`You currently have no bio.`")
        return

    try:
        await client(UpdateProfileRequest(about=match))
        await event.answer(
            "`Bio was successfully changed.`",
            log=("bio", f"Bio changed from {about} to {match}")
        )
    except AboutTooLongError:
        await event.answer("`The about text is too long.`")


@client.onMessage(
    command=("username", plugin_category),
    outgoing=True, regex="username(?: |$)(.*)$"
)
async def username(event):
    """Get your current username or update it."""
    match = event.matches[0].group(1)
    u1 = (await client.get_me()).username
    if not match:
        if u1:
            await event.answer(f"**{u1}**")
        else:
            await event.answer("`You currently have no username.`")
        return

    try:
        await client(UpdateUsernameRequest(username=match))
        await event.answer(
            f"`Successfully changed username to {match}`",
            log=("username", f"Username changed from {u1} to {match}")
        )
    except UsernameOccupiedError:
        await event.answer("`The username is already in use.`")
    except UsernameNotModifiedError:
        await event.answer("`The username was not modified.`")
    except UsernameInvalidError:
        await event.answer("`The username is invalid.`")


@client.onMessage(
    command=("pfp", plugin_category),
    outgoing=True, regex="pfp$"
)
async def pfp(event):
    """Get your current profile picture or update it."""
    reply = await event.get_reply_message()
    if not reply:
        photo = (await client(GetFullUserRequest("self"))).profile_photo
        if photo:
            await event.delete()
            await event.answer(file=photo)
        else:
            await event.answer("`You currently have no profile picture.`")
        return

    if not reply.media:
        await event.answer(
            "`What do I use to update the profile picture, a text?`"
        )
        return

    allowed = [MessageMediaDocument, MessageMediaPhoto]
    if type(reply.media) in allowed:
        try:
            temp_file = BytesIO()
            await client.download_media(reply, temp_file)
        except Exception as e:
            await event.answer(
                '`' + type(e).__name__ + ': ' + str(e) + '`',
                reply=True
                )
            temp_file.close()
            return
        temp_file.seek(0)
        photo = await client.upload_file(temp_file)
        temp_file.close()
    else:
        await event.answer("`Invalid media type.`")
        return

    try:
        await client(UploadProfilePhotoRequest(photo))
        await event.answer(
            "`Profile photo was successfully changed.`",
            log=("pfp", "Changed profile picture")
        )
    except FilePartsInvalidError:
        await event.answer("`The number of file parts is invalid.`")
    except ImageProcessFailedError:
        await event.answer("`Failure while processing image.`")
    except PhotoCropSizeSmallError:
        await event.answer("`Photo is too small.`")
    except PhotoExtInvalidError:
        await event.answer("`The extension of the photo is invalid.`")


@client.onMessage(
    command=("delpfp", plugin_category),
    outgoing=True, regex=r"delpfp(?: |$)(\d*|all)$"
)
async def delpfp(event):
    """Get your current profile picture count or delete them."""
    match = event.matches[0].group(1)
    if not match:
        count = (await client.get_profile_photos("self")).total
        amount = ("one profile picture." if count == 1
                  else f"{count} profile pictures.")
        await event.answer(f"`You currently have {amount}`")
        return

    await event.answer("`Processing all the profile pictures...`")
    limit = None if match == "all" else int(match)
    photos = await client.get_profile_photos("self", limit)
    count = len(photos)
    await client(DeletePhotosRequest(photos))
    amount = ("the current profile picture." if count == 1
              else f"{count} profile pictures.")
    text = f"`Successfully deleted {amount}`"
    await event.answer(
        text,
        log=("delpfp", f"Deleted {count} profile pciture(s)")
    )


@client.onMessage(
    command=("id", plugin_category),
    outgoing=True, regex=r"id(?: |$)(.*)$"
)
async def whichid(event):
    """Get the ID of a chat/channel or user."""
    match = event.matches[0].group(1).strip()
    if not match:
        entity = await event.get_chat()
    else:
        if match.isdigit():
            await event.answer("`Nice try, fool!`")
            return
        try:
            entity = await client.get_entity(match.strip())
        except Exception as e:
            await event.answer(
                f"`Error trying to fetch the entity:`\n```{e}```"
            )
            return
    await event.answer(
        f"`{get_display_name(entity)}:` `{get_peer_id(entity)}`"
    )
