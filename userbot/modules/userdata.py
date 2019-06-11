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


from io import BytesIO
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.types import ( InputPeerUser, InputPeerSelf, InputPhoto,
                                MessageMediaPhoto, MessageMediaDocument )
from telethon.errors import ( AboutTooLongError, FirstNameInvalidError,
                              UsernameInvalidError, UsernameNotModifiedError,
                              UsernameOccupiedError, FilePartsInvalidError,
                              ImageProcessFailedError, PhotoCropSizeSmallError,
                              PhotoExtInvalidError )

from userbot import client
from userbot.events import message
from userbot.helper_funcs.ids import get_user_from_entity
from userbot.helper_funcs.parser import parse_full_user
from userbot.helper_funcs.users import get_user_profile_pics


@message(outgoing=True, pattern="^.whois(?: |$)(.*)$")
async def whois(event):
    match = event.pattern_match.group(1)
    reply_id = None
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
    
    if event.reply_to_msg_id:
        reply_id = event.reply_to_msg_id
        if not match:
            reply = await event.get_reply_message()
            if reply.fwd_from:
                user = reply.fwd_from.from_id if reply.fwd_from.from_id else reply.sender_id
            else:
                user = reply.sender_id
    
    try:
        input_entity = await client.get_input_entity(user)
    except Exception as e:
        await event.edit(type(e).__name__ + ': ' + str(e))
        return

    allowed = [InputPeerUser, InputPeerSelf]
    if type(input_entity) not in allowed:
        await event.edit("Provided entity isn't a user.")
        return
    
    full_user = await client(GetFullUserRequest(input_entity))
    pfp, string = await parse_full_user(full_user)
    await event.delete()
    await event.respond(string, file=pfp, reply_to=reply_id)


@message(outgoing=True, pattern="^.name(?: |$)(.*)$")
async def name(event):
    match = event.pattern_match.group(1)
    if not match:
        me = await client.get_me()
        text = f"**First name:** `{me.first_name}`"
        if me.last_name:
            text += f"\n**Last name:** `{me.last_name}`"
        await event.edit(text)
        return

    split = match.split("last=")
    first = split[0]
    last = split[1] if len(split) is 2 else None

    try:
        await client(UpdateProfileRequest(
            first_name=first,
            last_name=last
        ))
        await event.edit("__Name was successfully changed.__")
    except FirstNameInvalidError:
        await event.edit("__The provided first name is invalid.__")


@message(outgoing=True, pattern="^.bio(?: |$)(.*)$")
async def bio(event):
    match = event.pattern_match.group(1)
    if not match:
        about = (await client(GetFullUserRequest("self"))).about
        if about:
            await event.edit(f"**{about}**")
        else:
            await event.edit("You currently have no bio.")
        return

    try:
        await client(UpdateProfileRequest(
            about=match
        ))
        await event.edit("__Bio was successfully changed.__")
    except AboutTooLongError:
        await event.edit("__The provided bio is too long.__")


@message(outgoing=True, pattern="^.username(?: |$)(.*)$")
async def username(event):
    match = event.pattern_match.group(1)
    if not match:
        username = (await client.get_me()).username
        if username:
            await event.edit(f"**{username}**")
        else:
            await event.edit("You currently have no username.")
        return

    try:
        await client(UpdateUsernameRequest(
            username=match
        ))
        await event.edit("__Username was successfully changed.__")
    except UsernameInvalidError:
        await event.edit("__Nobody is using this username, or the username is unacceptable.__")
    except UsernameNotModifiedError:
        await event.edit("__The provided username is not different from the current username.__")
    except UsernameOccupiedError:
        await event.edit("__The provided username is already taken.__")


@message(outgoing=True, pattern="^.pfp$")
async def pfp(event):
    reply = await event.get_reply_message()
    if not reply:
        photo = (await client(GetFullUserRequest("self"))).profile_photo
        if photo:
            await event.delete()
            await event.respond(file=photo)
        else:
            await event.edit("You currently have no profile picture.")
        return

    if not reply.media:
        await event.edit("What do I use to update the profile picture, a text?")
        return

    allowed = [MessageMediaDocument, MessageMediaPhoto]
    if type(reply.media) in allowed:
        try:
            temp_file = BytesIO()
            await client.download_media(reply, temp_file)
        except Exception as e:
            await event.edit(str(e))
            temp_file.close()
            return
        temp_file.seek(0)
        photo = await client.upload_file(temp_file)
        temp_file.close()
    else:
        await event.edit("__Invalid media type.__")
        return

    try:
        await client(UploadProfilePhotoRequest(photo))
        await event.edit("__Profile photo was successfully changed.__")
    except FilePartsInvalidError:
        await event.edit("__The number of file parts is invalid.__")
    except ImageProcessFailedError:
        await event.edit("__Failure while processing image.__")
    except PhotoCropSizeSmallError:
        await event.edit("__Photo is too small.__")
    except PhotoExtInvalidError:
        await event.edit("__The extension of the photo is invalid.__")


@message(outgoing=True, pattern=r"^.delpfp(?: |$)(\d*)")
async def delpfp(event):
    match = event.pattern_match.group(1)
    lim = int(match) if match else 0
    total = (await get_user_profile_pics("self", lim)).photos
    if not match:
        count = len(total)
        await event.edit(f"You currently have {count} profile pictures.")
        return

    await client(DeletePhotosRequest(total))
    amount = "current profile picture." if len(total) is 1 else f"{len(total)} profile pictures."
    text = f"__Successfully deleted {amount}__"
    await event.edit(text)