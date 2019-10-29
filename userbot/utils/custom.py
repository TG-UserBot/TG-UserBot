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
from logging import getLogger
from telethon.extensions import markdown
from telethon.tl import types, custom
from typing import Tuple


LOGGER = getLogger(__name__)


class Message(custom.Message):
    """Custom message type with the answer bound method"""

    def __init__(self, id, **kwargs):
        for k, v in kwargs.copy().items():
            if k.startswith('_'):
                del kwargs[k]
        super().__init__(id, **kwargs)

    async def answer(
        self,
        response,
        log: str or Tuple[str, str] = None,
        reply: bool = False,
        *args,
        **kwargs
    ) -> custom.Message:
        message = await self._client.get_messages(
            self.chat_id, ids=self.id
        )
        reply_to = self.reply_to_msg_id or self.id

        if isinstance(response, str):
            is_reply = reply or kwargs.get('reply_to', False)
            if len(response) < 4096:
                if is_reply or not (message and message.out):
                    kwargs.setdefault('reply_to', reply_to)
                    msg = await self.respond(response, *args, **kwargs)
                else:
                    msg = await self.edit(response, *args, **kwargs)
            else:
                if message and message.out:
                    await self.edit("`Output exceeded the limit.`")
                kwargs.setdefault('reply_to', reply_to)
                output = BytesIO(markdown.parse(response)[0].strip().encode())
                output.name = "output.txt"
                msg = await self.respond(
                    file=output,
                    *args,
                    **kwargs
                )
                output.close()
        else:
            kwargs.setdefault('reply_to', reply_to)
            msg = await self.respond(response, *args, **kwargs)

        if log:
            if isinstance(log, tuple):
                command, extra = log
                text = f"**USERBOT LOG** **#{command}**"
                if extra:
                    text += f"\n{extra}"
            else:
                text = f"**USERBOT LOG** `Executed command:` **#{log}**"
            if self._client.logger:
                entity = self._client.config['userbot'].getint(
                    'logger_group_id', False
                )
                if entity:
                    await self._client.send_message(entity, text)

        return msg


Message.register(types.Message)
# In-case you want a literal match for is instance
# Message.register(type(types.Message))
