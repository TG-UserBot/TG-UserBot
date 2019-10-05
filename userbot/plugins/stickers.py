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


import emoji
from io import BytesIO
from itertools import chain
from PIL import Image

from telethon.tl.types import DocumentAttributeSticker

from userbot import client


acceptable = []
default_emoji = u"🤔"
conversation_args = {
    'entity': '@Stickers',
    'timeout': 10,
    'exclusive': True
}
NO_PACK = """`Couldn't find {} in your sticker packs! \
Check your packs and update it in the config or use \
{}kang {}:<pack title> {} to make a new pack.`"""


@client.onMessage(
    command="getsticker", info="Get a stickers PNG or JPG",
    outgoing=True, regex="getsticker$"
)
async def getsticker(event):
    """Get sticker function used to convert a sticker for .getsticker"""
    if not event.reply_to_msg_id:
        await event.edit("`Reply to a sticker first.`")
        return

    reply = await event.get_reply_message()
    sticker = reply.sticker
    if not sticker:
        await event.edit("`This isn't a sticker, smh.`")
        return

    if sticker.mime_type == "application/x-tgsticker":
        await event.edit("`No point in uploading animated stickers.`")
        return
    else:
        sticker = BytesIO()
        await client.download_media(reply, sticker)
        pilImg = Image.open(sticker)
        pilImg.save(sticker, format="PNG")
        pilImg.close()
        sticker.seek(0)
        sticker.name = "sticcer.png"
        await reply.reply(file=sticker)

    await event.delete()


@client.onMessage(
    command="setdefaultpack", info="Set default packs for your stickers",
    outgoing=True, regex="setdefaultpack(?: |$)(.*)$"
)
async def setdefaultpacks(event):
    match = event.matches[0].group(1).strip()
    if not match:
        basic, animated = await _get_default_packs()
        text = "`Default kang packs:`\n**Basic:** `{}`\n**Animated:** `{}`"
        await event.edit(text.format(basic, animated))
        return

    if ':' in match:
        await event.edit(await _set_default_packs(match, ':'))
    elif '=' in match:
        await event.edit(await _set_default_packs(match, '='))
    else:
        client.config['userbot']['default_sticker_pack'] = match
        text = f"`Successfully changed your default pack to {match}!`"
        await event.edit(text)

    await client._updateconfig()


@client.onMessage(
    command="kang", info="Kang stickers or add images to your Sticker pack",
    outgoing=True, regex="kang(?: |$)(.*)$"
)
async def kang(event):
    """Steal stickers to your Sticker packs"""
    if event.reply_to_msg_id:
        sticker_event = await event.get_reply_message()
        if not await _is_sticker_event(sticker_event):
            await event.edit("`Invalid message type!`")
            return
    else:
        sticker_event = None
        async for msg in client.iter_messages(
            event.chat_id,
            offset_id=event.message.id,
            limit=10
        ):
            if await _is_sticker_event(msg):
                sticker_event = msg
                break
        if not sticker_event:
            await event.edit(
                "`Couldn't find any acceptable media in the recent messages.`"
            )
            return

    new_pack = False
    pack, emojis, name, is_animated = await _resolve_messages(
        event, sticker_event
    )
    if pack:
        if ':' in pack:
            pack, packnick = await _resolve_pack_name(pack, ':', is_animated)
            new_pack = True
        elif '=' in pack:
            pack, packnick = await _resolve_pack_name(pack, '=', is_animated)
            new_pack = True
        else:
            packs, first_msg = await _list_packs()
            is_pack = await _verify_cs_name(pack, packs)
            if not is_pack:
                await event.edit(
                    NO_PACK.format(
                        pack,
                        client.prefix,
                        pack or "<pack username>",
                        emojis or default_emoji
                    )
                )
                await _delete_sticker_messages(first_msg)
                return
    else:
        basic, animated = await _get_default_packs()
        packs, first_msg = await _list_packs()
        if is_animated:
            pack = await _verify_cs_name(animated, packs)
            if not pack:
                if "_kang_pack" in animated:
                    await event.edit("`Making a custom TG-UserBot pack!`")
                    user = await client.get_me()
                    tag = '@' + user.username if user.username else user.id
                    new_pack = True
                    pack = animated
                    packnick = f"{tag}'s animated kang pack"
                else:
                    pack = animated or "a default animated pack"
                    await event.edit(
                        f"`Couldn't find {pack} in your animated packs!`"
                    )
                    await _delete_sticker_messages(first_msg)
                    return
        else:
            pack = await _verify_cs_name(basic, packs)
            if not pack:
                if "_kang_pack" in basic:
                    await event.edit("`Making a custom TG-UserBot pack!`")
                    user = await client.get_me()
                    tag = '@' + user.username if user.username else user.id
                    new_pack = True
                    pack = basic
                    packnick = f"{tag}'s kang pack"
                else:
                    pack = basic or "a default pack"
                    await event.edit(
                        f"`Couldn't find {pack} in your "
                        "packs! Check your packs and update it in the config.`"
                    )
                    await _delete_sticker_messages(first_msg)
                    return

    async with client.conversation(**conversation_args) as conv:
        if new_pack:
            packtype = "/newanimated" if is_animated else "/newpack"
            await conv.send_message(packtype)
            await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(packnick)
            await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)
        else:
            await conv.send_message('/addsticker')
            await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(pack)
            r1 = await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)
            if "120 stickers" in r1.text:
                if "_kang_pack" in pack:
                    await event.edit(
                        "`Current userbot pack is full, making a new one!`"
                    )
                    await conv.send_message('/cancel')
                    await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)

                    pack, packnick = await _get_new_ub_pack(packs, is_animated)

                    packtype = "/newanimated" if is_animated else "/newpack"
                    await conv.send_message(packtype)
                    await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)
                    await conv.send_message(packnick)
                    await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)
                    new_pack = True
                else:
                    await event.edit(f"`{pack} has reached it's limit!`")
                    await _delete_sticker_messages(first_msg)
                    return
            elif ".TGS" in r1.text and not is_animated:
                await event.edit(
                    "`You're trying to kang a normal sticker "
                    "to an animated pack. Choose the correct pack!`"
                )
                await _delete_sticker_messages(first_msg)
                return
            elif ".PSD" in r1.text and is_animated:
                await event.edit(
                    "`You're trying to kang an animated sticker "
                    "to a normal pack. Choose the correct pack!`"
                )
                await _delete_sticker_messages(first_msg)
                return

        sticker = BytesIO()
        sticker.name = name
        await sticker_event.download_media(file=sticker)
        sticker.seek(0)
        if sticker_event.sticker:
            await conv.send_message(file=sticker, force_document=True)
        else:
            new_sticker = BytesIO()
            resized_sticker = await _resize_image(sticker, new_sticker)
            new_sticker.name = name
            new_sticker.seek(0)
            await conv.send_message(
                file=resized_sticker, force_document=True
            )
            new_sticker.close()

        sticker.close()
        await conv.get_response()
        await client.send_read_acknowledge(conv.chat_id)

        await conv.send_message(emojis)
        await conv.get_response()
        await client.send_read_acknowledge(conv.chat_id)
        if new_pack:
            await conv.send_message('/publish')
            await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)
            if is_animated:
                await conv.send_message('<' + packnick + '>')
                r2 = await conv.get_response()
                await client.send_read_acknowledge(conv.chat_id)

                if r2.text == "Invalid pack selected.":
                    await event.edit(
                        "`You tried to kang to an invalid pack.`"
                    )
                    await conv.send_message('/cancel')
                    await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)
                    return

            await conv.send_message('/skip')
            await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)

            await conv.send_message(pack)
            r2 = await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)
            if "Sorry" in r2.text:
                await conv.send_message('/cancel')
                await conv.get_response()
                await client.send_read_acknowledge(conv.chat_id)
                await event.edit(
                    "`Pack's short name is unacceptable or already taken. "
                    "Try thinking of a better short name.`"
                )
                await _delete_sticker_messages(first_msg)
                return
        else:
            await conv.send_message('/done')
            await conv.get_response()
            await client.send_read_acknowledge(conv.chat_id)

    await event.edit(
        "`Successfully added the sticker to` "
        f"[{pack}](https://t.me/addstickers/{pack})`!`"
    )
    await _delete_sticker_messages(first_msg)


async def _set_default_packs(string: str, delimiter: str) -> str:
    splits = string.split(delimiter)
    pack_type = splits[0].strip()
    name = ''.join(splits[1:]).strip()
    if pack_type.lower() == "animated":
        if name.lower() in ['reset', 'none']:
            text = f"`Successfully reset your default animated pack!`"
            del client.config['userbot']['default_animated_sticker_pack']
        else:
            client.config['userbot']['default_animated_sticker_pack'] = name
            text = (
                f"`Successfully changed your default animated pack to {name}!`"
            )
    elif pack_type.lower() == "basic":
        if name.lower() in ['reset', 'none']:
            text = f"`Successfully reset your default pack!`"
            del client.config['userbot']['default_sticker_pack']
        else:
            client.config['userbot']['default_sticker_pack'] = name
            text = f"`Successfully changed your default pack to {name}!`"
    else:
        text = "`Invalid pack type. Make sure it's animated or basic!`"

    return text


async def _delete_sticker_messages(offset):
    messages = [offset]
    async for msg in client.iter_messages(
        entity="@Stickers",
        offset_id=offset.id,
        reverse=True
    ):
        messages.append(msg)

    return await client.delete_messages('@Stickers', messages)


async def _get_new_ub_pack(packs: list, is_animated: bool):
    ub_packs = []
    for pack in packs:
        if "_kang_pack" in pack:
            if is_animated and "_animated" in pack:
                ub_packs = ub_packs.append(pack)
            if not is_animated and "_animated" not in pack:
                ub_packs = ub_packs.append(pack)

    pack = sorted(ub_packs)[-1]
    l_char = pack[-1:]
    if l_char.isdigit():
        pack = pack[:-1] + str(int(l_char) + 1)
    else:
        pack = pack + "_1"

    user = await client.get_me()
    tag = '@' + user.username if user.username else user.id
    if is_animated:
        packnick = f"{tag}'s animated kang pack {pack[-1:]}"
    else:
        packnick = f"{tag}'s kang pack {pack[-1:]}"

    return pack, packnick


async def _verify_cs_name(packname: str or None, packs: list):
    if not packname:
        return

    correct_pack = None
    for pack in packs:
        if pack.lower() == packname.lower():
            correct_pack = pack
            break
    return correct_pack


async def _resolve_pack_name(text: str, delimiter: str, is_animated: bool):
    splits = text.split(delimiter)
    packname = splits[0]
    packnickname = ''.join(splits[1:])

    if packname == "auto":
        user = (await client.get_me()).id
        if is_animated:
            packname = f"u{user}s_animated_kang_pack"
        else:
            packname = f"u{user}s_kang_pack"

    return packname, packnickname


async def _resize_image(image: BytesIO, new_image: BytesIO) -> BytesIO:
    image = Image.open(image)
    w, h = (image.width, image.height)

    if w == h:
        size = (512, 512)
    else:
        if w > 512:
            h = int(max(h * 512 / w, 1))
            w = int(512)
        if h > 512:
            w = int(max(w * 512 / h, 1))
            h = int(512)
        size = (w, h)

    image.resize(size).save(new_image, 'png')
    image.close()
    return new_image


async def _list_packs():
    async with client.conversation(**conversation_args) as conv:
        first = await conv.send_message('/cancel')
        await conv.get_response()
        await client.send_read_acknowledge(conv.chat_id)
        await conv.send_message('/packstats')
        buttons = (await conv.get_response()).buttons
        await client.send_read_acknowledge(conv.chat_id)
        buttons = list(chain.from_iterable(buttons))
        await conv.send_message('/cancel')
        await conv.get_response()
        await client.send_read_acknowledge(conv.chat_id)

        return [button.text for button in buttons], first


async def _extract_emojis(string):
    emojis = ''
    for e in string:
        if e in emoji.UNICODE_EMOJI and e not in emojis:
            emojis += e

    return emojis if len(emojis) > 0 else None


async def _extract_pack_name(string):
    name = ''
    for c in string:
        if c not in emoji.UNICODE_EMOJI:
            name += c

    return name.strip() if len(name) > 0 else None


async def _resolve_messages(event, sticker_event):
    sticker_name = "sticker.png"
    text = event.matches[0].group(1)
    is_animated = False
    atrribute_emojis = None

    if sticker_event.sticker:
        document = sticker_event.media.document
        atrribute_emojis = (
            attribute.alt
            for attribute in document.attributes
            if isinstance(attribute, DocumentAttributeSticker)
        )
        if document.mime_type == "application/x-tgsticker":
            sticker_name = 'AnimatedSticker.tgs'
            is_animated = True

    emojis_in_text = await _extract_emojis(text)
    pack_in_text = await _extract_pack_name(text)

    pack = None or pack_in_text
    emojis = emojis_in_text or atrribute_emojis or default_emoji

    return (pack, *emojis, sticker_name, is_animated)


async def _get_default_packs():
    user = await client.get_me()
    basic_default = f"u{user.id}s_kang_pack"
    animated_default = f"u{user.id}s_animated_kang_pack"
    config = client.config['userbot']
    basic = config.get('default_sticker_pack', basic_default)
    animated = config.get('default_animated_sticker_pack', animated_default)

    return basic, animated


async def _is_sticker_event(event) -> bool:
    if event.sticker or event.photo:
        return True
    if event.document and "image" in event.media.document.mime_type:
        return True

    return False
