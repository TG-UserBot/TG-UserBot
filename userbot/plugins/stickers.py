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
from os.path import isfile
from PIL import Image

from userbot.events import basic_command, commands


@commands("getsticker")
@basic_command(command="getsticker$")
async def getsticker(client, event):
    """Get sticker function used to convert a sticker for .getsticker"""
    reply = event.reply_to_message
    if not reply:
        await event.edit("`Reply to a sticker first.`")
        return

    sticker = reply.sticker
    if not sticker:
        await event.edit("`This isn't a sticker, smh.`")
        return

    if isfile("sticker.png"):
        remove("sticker.png")

    if sticker.mime_type == "application/x-tgsticker":
        await event.edit("`No point in uploading animated stickers.`")
        return
    else:
        webp = await client.download_media(reply)
        pilImg = Image.open(webp)
        pilImg.save("sticker.png", format="PNG")
        pilImg.close()
        await reply.reply_document("sticker.png")
        remove(webp)
        remove("sticker.png")

    await event.delete()
