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


import datetime
import re
import io
import itertools
import PIL
from typing import BinaryIO, List, Sequence, Tuple, Union

from telethon.tl import functions, types

from userbot import client, LOGGER
from userbot.utils.helpers import get_chat_link
from userbot.utils.events import NewMessage


plugin_category = "stickers"
acceptable = []
default_emoji = "🤔"
conversation_args = {
    'entity': '@Stickers',
    'timeout': 10,
    'exclusive': True
}
DEFAULT_MUTE = types.InputPeerNotifySettings(
    silent=True,
    mute_until=datetime.timedelta(days=365)
)

NO_PACK = """`Couldn't find {} in your sticker packs! \
Check your packs and update it in the config or use \
{}kang {}:<pack title> {} to make a new pack.`"""

FALSE_DEFAULT = """`Couldn't find {} in your \
packs! Check your packs and update it in the config \
or use {}stickerpack reset for deafult packs.`"""


@client.onMessage(
    command=("getsticker", plugin_category),
    outgoing=True, regex="getsticker(?: |$)(file|document)?$"
)
async def getsticker(event: NewMessage.Event) -> None:
    """Convert a sticker to a png and also send it as a file if specified."""
    if not event.reply_to_msg_id:
        await event.answer("`Reply to a sticker first.`")
        return

    reply = await event.get_reply_message()
    sticker = reply.sticker
    if not sticker:
        await event.answer("`This isn't a sticker, smh.`")
        return

    if sticker.mime_type == "application/x-tgsticker":
        await event.answer("`No point in uploading animated stickers.`")
        return
    else:
        sticker_bytes = io.BytesIO()
        await reply.download_media(sticker_bytes)
        sticker = io.BytesIO()
        try:
            pilImg = PIL.Image.open(sticker_bytes)
        except OSError as e:
            await event.answer(f'`OSError: {e}`')
            return
        pilImg.save(sticker, format="PNG")
        pilImg.close()
        sticker.name = "sticcer.png"
        sticker.seek(0)
        if event.matches[0].group(1):
            await reply.reply(file=sticker, force_document=True)
        else:
            await reply.reply(file=sticker)
        sticker_bytes.close()
        sticker.close()

    await event.delete()


@client.onMessage(
    command=("stickerpack", plugin_category),
    outgoing=True, regex=r"stickerpack(?: |$)(.*)"
)
async def stickerpack(event: NewMessage.Event) -> None:
    """Get your default kang's sticker packs or update them."""
    match = event.matches[0].group(1) or ''
    if not match:
        basic, animated = await _get_default_packs()
        basic = f"[{basic}](https://t.me/addstickers/{basic})"
        animated = f"[{animated}](https://t.me/addstickers/{animated})"
        text = "`Default kang packs:`\n**Basic:** {}\n**Animated:** {}"
        await event.answer(text.format(basic, animated))
        return

    args, kwargs = await client.parse_arguments(match)
    if kwargs:
        texts = []
        for x, y in kwargs.itmes():
            texts.append(await _set_default_packs(x, y))
        text = '\n'.join(texts)
    elif "reset" in args:
        await _set_default_packs('basic', 'reset')
        await _set_default_packs('animated', 'reset')
        text = "`Successfully reset both of your packs.`"
    else:
        text = await _set_default_packs(f"basic", args[0])
    await event.answer(text, log=("stickerpack", text))


@client.onMessage(
    command=("delsticker", plugin_category),
    outgoing=True, regex="delsticker$"
)
async def delsticker(event: NewMessage.Event) -> None:
    """Remove a sticker from your existing pack."""
    if not event.reply_to_msg_id:
        await event.answer("`Reply to a sticker to delete it.`")
        return

    reply = await event.get_reply_message()
    if not reply.sticker:
        await event.answer("`Replied to message isn't a sticker.`")
        return

    stickerset = None
    for a in reply.document.attributes:
        if isinstance(a, types.DocumentAttributeSticker):
            stickerset = a.stickerset
            break

    if not stickerset:
        await event.answer("`Couldn't find the sticker set.`")
        return

    result = await client(functions.messages.GetStickerSetRequest(
        stickerset=stickerset
    ))
    short_name = result.set.short_name
    notif = await client(functions.account.GetNotifySettingsRequest(
        peer="Stickers"
    ))
    await _update_stickers_notif(DEFAULT_MUTE)
    await event.answer("`Fetching all your sticker packs.`")
    packs, first_msg = await _list_packs()
    target_pack = None
    for pack in packs:
        if short_name in pack:
            target_pack = pack
            break

    if not target_pack:
        await event.answer("`Couldn't find the specified set in your packs.`")
        await _delete_sticker_messages(first_msg)
        await _update_stickers_notif(notif)
        return

    await event.answer("`Deleting the sticker from your pack.`")
    async with client.conversation(**conversation_args) as conv:
        await conv.send_message('/delsticker')
        await conv.get_response()
        await conv.send_message(target_pack)
        r1 = await conv.get_response()
        LOGGER.debug("Stickers:" + r1.text)
        await reply.forward_to("@Stickers")
        r2 = await conv.get_response()
        LOGGER.debug("Stickers:" + r2.text)
        if "I have deleted that sticker for you" in r2.text:
            status = True
        else:
            status = r2.text
        await conv.send_message('/cancel')
        await conv.get_response()

    if status is True:
        pack = f"[{short_name}](https://t.me/addstickers/{short_name})"
        await event.answer(
            f"`Successfully removed the sticker from` {pack}"
        )
        await _delete_sticker_messages(first_msg)
    else:
        await event.answer(
            f"**Couldn't delete the sticker. Perhaps it's not in your pack.**"
            "\n`Check the chat with @Stickers for more information.`"
        )
        await client.send_read_acknowledge("@Stickers")
    await _update_stickers_notif(notif)


@client.onMessage(
    command=("kang", plugin_category),
    outgoing=True, regex=r"kang(?: |$)(.*)"
)
async def kang(event: NewMessage.Event) -> None:
    """Steal (AKA kang) stickers and images to your Sticker packs."""
    match = event.matches[0].group(1) or ''
    if event.reply_to_msg_id:
        sticker_event = await event.get_reply_message()
        if not await _is_sticker_event(sticker_event):
            await event.answer("`Invalid message type!`")
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
            await event.answer(
                "`Couldn't find any acceptable media in the recent messages.`"
            )
            return

    new_pack = False
    first_msg = None
    new_first_msg = None
    args, kwargs = await client.parse_arguments(match)
    pack, emojis, name, is_animated = await _resolve_messages(
        args, kwargs, sticker_event
    )
    prefix = client.prefix if client.prefix is not None else '.'
    notif = await client(functions.account.GetNotifySettingsRequest(
        peer="Stickers"
    ))
    await _update_stickers_notif(DEFAULT_MUTE)
    if pack or len(kwargs) == 1:
        if pack and pack.lower() == "auto":
            pack, packnick = await _get_userbot_auto_pack(is_animated)
        if kwargs:
            pack = None
            packnick = None
            for x, y in kwargs.items():
                pack = str(x)
                packnick = str(y)
            if not (pack and packnick):
                await event.answer(
                    "`Are you sure you're using the correct syntax?`\n"
                    f"`{prefix}kang <packName>=<packsShortName>`\n"
                    "`You can also choose emojis whilst making a new pack.`"
                )
                await _update_stickers_notif(notif)
                return
            packs, first_msg = await _list_packs()
            is_pack = await _verify_cs_name(pack, packs)
            if is_pack:
                pack = is_pack
                new_pack = False
            else:
                new_pack = True
            attribute_emoji = None
            if sticker_event.sticker:
                for attribute in sticker_event.media.document.attributes:
                    if isinstance(attribute, types.DocumentAttributeSticker):
                        attribute_emoji = attribute.alt
            if attribute_emoji:
                if emojis and attribute_emoji not in emojis:
                    emojis += attribute_emoji
                else:
                    emojis = attribute_emoji
        else:
            packs, first_msg = await _list_packs()
            is_pack = await _verify_cs_name(pack, packs)
            if "_kang_pack" in pack:
                new_pack = True
            elif not is_pack:
                await event.answer(
                    NO_PACK.format(
                        pack,
                        prefix,
                        pack or "<pack username>",
                        emojis or default_emoji
                    )
                )
                await _delete_sticker_messages(first_msg)
                await _update_stickers_notif(notif)
                return
            else:
                pack = is_pack
    else:
        basic, animated = await _get_default_packs()
        packs, first_msg = await _list_packs()
        if is_animated:
            pack = await _verify_cs_name(animated, packs)
            if not pack:
                if "_kang_pack" in animated:
                    await event.answer("`Making a custom TG-UserBot pack!`")
                    pack = animated
                    _, packnick = await _get_userbot_auto_pack(is_animated)
                    new_pack = True
                else:
                    pack = animated or "a default animated pack"
                    await event.answer(FALSE_DEFAULT.format(pack, prefix))
                    await _delete_sticker_messages(first_msg)
                    await _update_stickers_notif(notif)
                    return
        else:
            pack = await _verify_cs_name(basic, packs)
            if not pack:
                if "_kang_pack" in basic:
                    await event.answer("`Making a custom TG-UserBot pack!`")
                    pack = basic
                    _, packnick = await _get_userbot_auto_pack(is_animated)
                    new_pack = True
                else:
                    pack = basic or "a default pack"
                    await event.answer(FALSE_DEFAULT.format(pack, prefix))
                    await _delete_sticker_messages(first_msg)
                    await _update_stickers_notif(notif)
                    return

    await event.answer(
        "`Turning on the kang machine... Your sticker? My sticker!`"
    )
    async with client.conversation(**conversation_args) as conv:
        if new_pack:
            packtype = "/newanimated" if is_animated else "/newpack"
            new_first_msg = await conv.send_message(packtype)
            r1 = await conv.get_response()
            LOGGER.debug("Stickers:" + r1.text)
            await client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(packnick)
            r2 = await conv.get_response()
            LOGGER.debug("Stickers:" + r2.text)
            await client.send_read_acknowledge(conv.chat_id)
        else:
            await conv.send_message('/addsticker')
            r1 = await conv.get_response()
            LOGGER.debug("Stickers:" + r1.text)
            await client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(pack)
            r2 = await conv.get_response()
            LOGGER.debug("Stickers:" + r2.text)
            await client.send_read_acknowledge(conv.chat_id)
            if "120 stickers" in r2.text:
                if "_kang_pack" in pack:
                    await event.answer(
                        "`Current userbot pack is full, making a new one!`"
                    )
                    await conv.send_message('/cancel')
                    r11 = await conv.get_response()
                    LOGGER.debug("Stickers:" + r11.text)
                    await client.send_read_acknowledge(conv.chat_id)

                    pack, packnick = await _get_new_ub_pack(packs, is_animated)

                    packtype = "/newanimated" if is_animated else "/newpack"
                    await conv.send_message(packtype)
                    r12 = await conv.get_response()
                    LOGGER.debug("Stickers:" + r12.text)
                    await client.send_read_acknowledge(conv.chat_id)
                    await conv.send_message(packnick)
                    r13 = await conv.get_response()
                    LOGGER.debug("Stickers:" + r13.text)
                    await client.send_read_acknowledge(conv.chat_id)
                    new_pack = True
                else:
                    await event.answer(f"`{pack} has reached it's limit!`")
                    await _delete_sticker_messages(first_msg or new_first_msg)
                    await _update_stickers_notif(notif)
                    return
            elif ".TGS" in r2.text and not is_animated:
                await event.answer(
                    "`You're trying to kang a normal sticker "
                    "to an animated pack. Choose the correct pack!`"
                )
                await _delete_sticker_messages(first_msg or new_first_msg)
                await _update_stickers_notif(notif)
                return
            elif ".PSD" in r2.text and is_animated:
                await event.answer(
                    "`You're trying to kang an animated sticker "
                    "to a normal pack. Choose the correct pack!`"
                )
                await _delete_sticker_messages(first_msg or new_first_msg)
                await _update_stickers_notif(notif)
                return

        sticker = io.BytesIO()
        sticker.name = name
        await sticker_event.download_media(file=sticker)
        if (
            sticker_event.sticker and
            sticker_event.sticker.mime_type == "application/x-tgsticker"
        ):
            sticker.seek(0)
            await conv.send_message(
                file=sticker, force_document=True
            )
        else:
            new_sticker = io.BytesIO()
            if sticker_event.sticker:
                resized_sticker = await _resize_image(
                    sticker, new_sticker, False
                )
            else:
                resized_sticker = await _resize_image(sticker, new_sticker)
            if isinstance(resized_sticker, str):
                await event.answer(resized_sticker)
                await _update_stickers_notif(notif)
                return
            await conv.send_message(
                file=new_sticker, force_document=True
            )
            new_sticker.close()
        sticker.close()
        r3 = await conv.get_response()
        LOGGER.debug("Stickers:" + r3.text)
        await client.send_read_acknowledge(conv.chat_id)

        await conv.send_message(emojis)
        r4 = await conv.get_response()
        LOGGER.debug("Stickers:" + r4.text)
        await client.send_read_acknowledge(conv.chat_id)
        if new_pack:
            await conv.send_message('/publish')
            r5 = await conv.get_response()
            LOGGER.debug("Stickers:" + r5.text)
            await client.send_read_acknowledge(conv.chat_id)
            if is_animated:
                await conv.send_message('<' + packnick + '>')
                r41 = await conv.get_response()
                LOGGER.debug("Stickers:" + r41.text)
                await client.send_read_acknowledge(conv.chat_id)

                if r41.text == "Invalid pack selected.":
                    await event.answer(
                        "`You tried to kang to an invalid pack.`"
                    )
                    await conv.send_message('/cancel')
                    await conv.get_response()
                    await client.send_read_acknowledge(conv.chat_id)
                    await _update_stickers_notif(notif)
                    return

            await conv.send_message('/skip')
            r6 = await conv.get_response()
            LOGGER.debug("Stickers:" + r6.text)
            await client.send_read_acknowledge(conv.chat_id)

            await conv.send_message(pack)
            r7 = await conv.get_response()
            LOGGER.debug("Stickers:" + r7.text)
            await client.send_read_acknowledge(conv.chat_id)
            if "Sorry" in r7.text:
                await conv.send_message('/cancel')
                r61 = await conv.get_response()
                LOGGER.debug("Stickers:" + r61.text)
                await client.send_read_acknowledge(conv.chat_id)
                await event.answer(
                    "`Pack's short name is unacceptable or already taken. "
                    "Try thinking of a better short name.`"
                )
                await _delete_sticker_messages(first_msg or new_first_msg)
                await _update_stickers_notif(notif)
                return
        else:
            await conv.send_message('/done')
            r5 = await conv.get_response()
            LOGGER.debug("Stickers:" + r5.text)
            await client.send_read_acknowledge(conv.chat_id)

    pack = f"[{pack}](https://t.me/addstickers/{pack})"
    extra = await get_chat_link(event, sticker_event.id)
    await event.answer(
        f"`Successfully added the sticker to` {pack} `!`",
        self_destruct=4,
        log=("kang", f"Successfully kanged a sticker from {extra} to {pack}")
    )
    await _delete_sticker_messages(first_msg or new_first_msg)
    await _update_stickers_notif(notif)


async def _set_default_packs(pack_type: str, name: str) -> str:
    if pack_type.lower() == "animated":
        if name.lower() in ['reset', 'none']:
            is_pack = client.config['userbot'].get(
                'default_animated_sticker_pack', None
            )
            if is_pack:
                text = f"`Successfully reset your default animated pack!`"
                del client.config['userbot']['default_animated_sticker_pack']
            else:
                text = "`You had no default animated pack to reset!`"
        else:
            client.config['userbot']['default_animated_sticker_pack'] = name
            text = (
                f"`Successfully changed your default animated pack to {name}!`"
            )
    elif pack_type.lower() == "basic":
        if name.lower() in ['reset', 'none']:
            is_pack = client.config['userbot'].get(
                'default_sticker_pack', None
            )
            if is_pack:
                text = f"`Successfully reset your default pack!`"
                del client.config['userbot']['default_sticker_pack']
            else:
                text = "`You had no default pack to reset!`"
        else:
            client.config['userbot']['default_sticker_pack'] = name
            text = f"`Successfully changed your default pack to {name}!`"
    else:
        text = "`Invalid pack type. Make sure it's animated or basic!`"
    client._updateconfig()
    return text


async def _delete_sticker_messages(
    message: types.Message
) -> Sequence[types.messages.AffectedMessages]:
    messages = [message]
    async for msg in client.iter_messages(
        entity="@Stickers",
        offset_id=message.id,
        reverse=True
    ):
        messages.append(msg)

    return await client.delete_messages('@Stickers', messages)


async def _get_new_ub_pack(packs: list, is_animated: bool) -> Tuple[str, str]:
    ub_packs = []
    for pack in packs:
        if "_kang_pack" in pack:
            if "_animated" in pack:
                if is_animated:
                    ub_packs = ub_packs.append(pack)
            else:
                if not is_animated:
                    ub_packs = ub_packs.append(pack)

    pack = sorted(ub_packs)[-1]  # Fetch the last pack
    l_char = pack[-1:]  # Check if the suffix is a digit
    if l_char.isdigit():
        pack = pack[:-1] + str(int(l_char) + 1)  # ++ the suffix
    else:
        pack = pack + "_1"  # Append the suffix

    user = await client.get_me()
    tag = '@' + user.username if user.username else user.id
    if is_animated:
        packnick = f"{tag}'s animated kang pack {pack[-1:]}"
    else:
        packnick = f"{tag}'s kang pack {pack[-1:]}"

    return pack, packnick


async def _verify_cs_name(packname: str or None, packs: list) -> str:
    if not packs:
        return
    if not packname:
        return

    correct_pack = None
    for pack in packs:
        if pack.lower() == packname.lower():
            correct_pack = pack
            break
    return correct_pack


async def _resize_image(
    image: BinaryIO,
    new_image: BinaryIO,
    resize: bool = True
) -> BinaryIO:
    try:
        name = image.name
        image = PIL.Image.open(image)
    except OSError as e:
        return f"`OSError: {e}`"

    if resize:
        w, h = (image.width, image.height)
        if w == h:
            size = (512, 512)
        else:
            if w > h:
                h = int(max(h * 512 / w, 1))
                w = int(512)
            else:
                w = int(max(w * 512 / h, 1))
                h = int(512)
            size = (w, h)
        image.resize(size).save(new_image, 'png')
    else:
        image.save(new_image, 'png')

    del image  # Nothing to close once the image is loaded.
    new_image.name = name
    new_image.seek(0)

    return new_image


async def _list_packs() -> Tuple[List[str], types.Message]:
    async with client.conversation(**conversation_args) as conv:
        first = await conv.send_message('/cancel')
        r1 = await conv.get_response()
        LOGGER.debug("Stickers:" + r1.text)
        await client.send_read_acknowledge(conv.chat_id)
        await conv.send_message('/packstats')
        r2 = await conv.get_response()
        LOGGER.debug("Stickers:" + r2.text)
        if r2.text.startswith("You don't have any sticker packs yet."):
            return [], first
        await client.send_read_acknowledge(conv.chat_id)
        buttons = list(itertools.chain.from_iterable(r2.buttons))
        await conv.send_message('/cancel')
        r3 = await conv.get_response()
        LOGGER.debug("Stickers:" + r3.text)
        await client.send_read_acknowledge(conv.chat_id)

        return [button.text for button in buttons], first


async def _resolve_messages(
    args: list, kwargs: dict, sticker_event: types.Message
) -> Tuple[Union[str, None], str, str, bool]:
    sticker_name = "sticker.png"
    pack = None
    is_animated = False
    attribute_emoji = None
    packs = kwargs.pop('pack', [])
    _emojis = kwargs.pop('emojis', '')

    if sticker_event.sticker:
        document = sticker_event.media.document
        for attribute in document.attributes:
            if isinstance(attribute, types.DocumentAttributeSticker):
                attribute_emoji = attribute.alt
        if document.mime_type == "application/x-tgsticker":
            sticker_name = 'AnimatedSticker.tgs'
            is_animated = True

    for i in args:
        if re.search(r'[^\w\s,]', i):
            _emojis += i
        else:
            packs.append(i)

    if len(packs) == 1:
        pack = packs[0]

    emojis = _emojis or attribute_emoji or default_emoji

    return pack, emojis, sticker_name, is_animated


async def _get_default_packs() -> Tuple[str, str]:
    user = await client.get_me()
    basic_default = f"u{user.id}s_kang_pack"
    animated_default = f"u{user.id}s_animated_kang_pack"
    config = client.config['userbot']
    basic = config.get('default_sticker_pack', basic_default)
    animated = config.get('default_animated_sticker_pack', animated_default)

    if basic.strip().lower() == "auto" or basic.strip().lower() == "none":
        basic = basic_default
    if (
        animated.strip().lower() == "auto" or
        animated.strip().lower() == "none"
    ):
        animated = animated_default

    return basic, animated


async def _is_sticker_event(event: NewMessage.Event) -> bool:
    if event.sticker or event.photo:
        return True
    if event.document and "image" in event.document.mime_type:
        return True

    return False


async def _update_stickers_notif(notif: types.PeerNotifySettings) -> None:
    await client(functions.account.UpdateNotifySettingsRequest(
        peer="Stickers",
        settings=types.InputPeerNotifySettings(**vars(notif))
    ))


async def _get_userbot_auto_pack(is_animated: bool = False) -> str:
    user = await client.get_me()
    tag = '@' + user.username if user.username else user.id
    if is_animated:
        pack = f"u{user.id}s_animated_kang_pack"
        packnick = f"{tag}'s animated kang pack"
    else:
        pack = f"u{user.id}s_kang_pack"
        packnick = f"{tag}'s kang pack"
    return pack, packnick
