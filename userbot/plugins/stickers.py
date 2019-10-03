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
from PIL import Image

from userbot import client


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
