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


from pyrogram.api.functions.help import GetNearestDc

from userbot.events import outgoing


@outgoing(pattern="dc$")
async def dc(client, event):
    result = await client.send(GetNearestDc())
    text = (
        f"**Country:** `{result.country}`\n" +
        f"**This DC:** `{result.this_dc}`\n" +
        f"**Nearest DC:** `{result.nearest_dc}`"
    )
    await event.edit(text)