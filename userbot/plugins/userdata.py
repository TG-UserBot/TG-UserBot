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


import io
import PIL

from telethon import errors
from telethon.utils import get_display_name, get_peer_id
from telethon.tl import functions, types

from userbot import client, LOGGER
from userbot.helper_funcs.parser import Parser
from userbot.utils.events import NewMessage


plugin_category = "user"


@client.onMessage(
    command=("whois", plugin_category),
    outgoing=True, regex=r"(?:who|what)is(?: |$)([\s\S]*)"
)
async def whois(event: NewMessage.Event) -> None:
    """Get your or a user's/chat's information."""
    match = event.matches[0].group(1)
    entities = []

    if match:
        entities, _ = await client.parse_arguments(match)
        if "this" in entities:
            entities.remove("this")
            entities.append(event.chat_id)
    else:
        entities.append("self")

    if event.reply_to_msg_id:
        if not entities:
            reply = await event.get_reply_message()
            user = reply.sender_id
            if reply.fwd_from:
                if reply.fwd_from.from_id:
                    user = reply.fwd_from.from_id

    users = ""
    chats = ""
    channels = ""
    failed = []
    for user in entities:
        try:
            input_entity = await client.get_input_entity(user)
            if isinstance(input_entity, types.InputPeerChat):
                full_chat = await client(
                    functions.messages.GetFullChatRequest(input_entity)
                )
                string = await Parser.parse_full_chat(full_chat, event)
                chats += f"\n{chats}\n"
            elif isinstance(input_entity, types.InputPeerChannel):
                full_channel = await client(
                    functions.channels.GetFullChannelRequest(input_entity)
                )
                string = await Parser.parse_full_chat(full_channel, event)
                channels += f"\n{string}\n"
            else:
                full_user = await client(
                    functions.users.GetFullUserRequest(input_entity)
                )
                string = await Parser.parse_full_user(full_user, event)
                users += f"\n{string}\n"
        except Exception as e:
            LOGGER.debug(e)
            failed.append(user)

    if users:
        await event.answer("**USERS**" + users, reply=True)
    if chats:
        await event.answer("**CHATS**" + chats, reply=True)
    if channels:
        await event.answer("**CHANNELS**" + channels, reply=True)

    if failed:
        failedtext = "**Unable to fetch:**\n"
        failedtext += ", ".join(f'`{u}`' for u in failed)
        await event.answer(failedtext)
    elif not (users or chats or channels):
        await event.answer("__Something went wrong!__", self_destruct=2)


@client.onMessage(
    command=("name", plugin_category),
    outgoing=True, regex="name(?: |$)(.*)$"
)
async def name(event: NewMessage.Event) -> None:
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
    last = ' '.join(split[1:]) if len(split) > 1 else ''
    n1 = get_display_name(await client.get_me())

    try:
        await client(functions.account.UpdateProfileRequest(
            first_name=first,
            last_name=last
        ))
        n2 = get_display_name(await client.get_me())
        await event.answer(
            f"`Name was successfully changed to {n2}.`",
            log=("name", f"Name changed from {n1} to {n2}")
        )
    except errors.FirstNameInvalidError:
        await event.answer("`The first name is invalid.`")
    except Exception as e:
        await event.answer('`' + type(e).__name__ + ': ' + str(e) + '`')


@client.onMessage(
    command=("bio", plugin_category),
    outgoing=True, regex="bio(?: |$)(.*)$"
)
async def bio(event: NewMessage.Event) -> None:
    """Get your current bio or update it."""
    match = event.matches[0].group(1)
    about = (await client(functions.users.GetFullUserRequest("self"))).about
    if not match:
        if about:
            await event.answer(f"**{about}**")
        else:
            await event.answer("`You currently have no bio.`")
        return

    try:
        await client(functions.account.UpdateProfileRequest(about=match))
        await event.answer(
            f"`Bio was successfully changed to {match}.`",
            log=("bio", f"Bio changed from {about} to {match}")
        )
    except errors.AboutTooLongError:
        await event.answer("`The about text is too long.`")


@client.onMessage(
    command=("username", plugin_category),
    outgoing=True, regex="username(?: |$)(.*)$"
)
async def username(event: NewMessage.Event) -> None:
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
        await client(functions.account.UpdateUsernameRequest(username=match))
        await event.answer(
            f"`Username was successfully changed to {match}`",
            log=("username", f"Username changed from {u1} to {match}")
        )
    except errors.UsernameOccupiedError:
        await event.answer("`The username is already in use.`")
    except errors.UsernameNotModifiedError:
        await event.answer("`The username was not modified.`")
    except errors.UsernameInvalidError:
        await event.answer("`The username is invalid.`")


@client.onMessage(
    command=("pfp", plugin_category),
    outgoing=True, regex="pfp$"
)
async def pfp(event: NewMessage.Event) -> None:
    """Get your current profile picture or update it."""
    reply = await event.get_reply_message()
    if not reply:
        photo = await client(functions.users.GetFullUserRequest("self"))
        photo = photo.profile_photo
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

    if (
        (reply.document and reply.document.mime_type.startswith("image")) or
        reply.photo or reply.sticker
    ):
        if reply.sticker and not reply.sticker.mime_type == "image/webp":
            await event.answer("`Invalid sticker type.`")
            return
        try:
            temp_file = io.BytesIO()
            await client.download_media(reply, temp_file)
        except Exception as e:
            await event.answer(
                '`' + type(e).__name__ + ': ' + str(e) + '`',
                reply=True
                )
            temp_file.close()
            return
        temp_file.seek(0)
        if reply.sticker:
            sticker = io.BytesIO()
            pilImg = PIL.Image.open(temp_file)
            pilImg.save(sticker, format="PNG")
            pilImg.close()
            sticker.seek(0)
            sticker.name = "sticcer.png"
            photo = await client.upload_file(sticker)
            temp_file.close()
            sticker.close()
        else:
            photo = await client.upload_file(temp_file)
            temp_file.close()
    else:
        await event.answer("`Invalid media type.`")
        return

    try:
        await client(functions.photos.UploadProfilePhotoRequest(photo))
        await event.answer(
            "`Profile photo was successfully changed.`",
            log=("pfp", "Changed profile picture")
        )
    except errors.FilePartsInvalidError:
        await event.answer("`The number of file parts is invalid.`")
    except errors.ImageProcessFailedError:
        await event.answer("`Failure while processing image.`")
    except errors.PhotoCropSizeSmallError:
        await event.answer("`Photo is too small.`")
    except errors.PhotoExtInvalidError:
        await event.answer("`The extension of the photo is invalid.`")


@client.onMessage(
    command=("delpfp", plugin_category),
    outgoing=True, regex=r"delpfp(?: |$)(\d*|all)$"
)
async def delpfp(event: NewMessage.Event) -> None:
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
    await client(functions.photos.DeletePhotosRequest(photos))
    amount = ("the current profile picture." if count == 1
              else f"{count} profile pictures.")
    text = f"`Successfully deleted {amount}`"
    await event.answer(
        text,
        log=("delpfp", f"Deleted {count} profile picture(s)")
    )


@client.onMessage(
    command=("id", plugin_category),
    outgoing=True, regex=r"id(?: |$)([\s\S]*)"
)
async def whichid(event: NewMessage.Event) -> None:
    """Get the ID of a chat/channel or user."""
    match = event.matches[0].group(1)
    text = ""
    if not match and not event.reply_to_msg_id:
        if event.chat:
            text = f"{event.chat.title}: "
        text += f"`{get_peer_id(event.chat_id)}`"
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        user = reply.sender_id
        if reply.fwd_from:
            if reply.fwd_from.from_id:
                user = reply.fwd_from.from_id
        text = f"`{get_peer_id(user)}`"
    else:
        failed = []
        strings = []
        users, _ = await client.parse_arguments(match)
        for user in users:
            try:
                entity = await client.get_input_entity(user)
                strings.append(f"{user}: `{get_peer_id(entity)}`")
            except Exception as e:
                failed.append(user)
                LOGGER.debug(e)
        if strings:
            text = ",\n".join(strings)
        if failed:
            ftext = "**Users which weren't resolved:**\n"
            ftext += ", ".join(f'`{f}`' for f in failed)
            await event.answer(ftext, reply=True)
    if text:
        await event.answer(text)
