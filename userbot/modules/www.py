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


from telethon.tl.functions.help import GetNearestDcRequest

from userbot import client
from userbot.events import message


@message(outgoing=True, pattern=r"^.dc$")
async def dc(event):
    result = await client(GetNearestDcRequest())
    text = (
        f"**Country:** __{result.country}__\n" +
        f"**This DC:** __{result.this_dc}__\n" +
        f"**Nearest DC:** __{result.nearest_dc}__"
    )
    await event.edit(text)