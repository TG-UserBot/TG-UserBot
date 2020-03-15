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


import re
from typing import Tuple

from telethon import events
from telethon.tl import custom, functions, types

from .custom import answer


custom.Message.answer = answer


@events.common.name_inner_event
class NewMessage(events.NewMessage):
    """Custom NewMessage event inheriting the default Telethon event"""

    def __init__(
        self,
        disable_prefix: bool = None,
        regex: Tuple[str, int] or str = None,
        require_admin: bool = None,
        **kwargs
    ):
        """Overriding the default init to add additional attributes"""
        super().__init__(**kwargs)

        if regex:
            if isinstance(regex, tuple):
                exp, flags = regex
                if isinstance(exp, tuple):
                    raise TypeError(
                        "Make sure you're using a string for a pattern!"
                    )
                self.regex = (exp, flags)
            elif isinstance(regex, str):
                self.regex = (regex, 0)
            else:
                raise TypeError("Invalid regex type given!")
        else:
            self.regex = regex

        self.disable_prefix = disable_prefix
        self.require_admin = require_admin

    def filter(self, event):
        """Overriding the default filter to check additional values"""
        event = super().filter(event)
        if not event:
            return

        if event._client.prefix:
            prefix = re.escape(event._client.prefix)
        else:
            prefix = r"[^/!#@\$A-Za-z0-9]"

        if self.regex:
            exp, flags = self.regex

            if not self.disable_prefix:
                pattern = re.compile(
                    "(?i)^" + prefix + exp,
                    flags=flags
                ).finditer
            else:
                pattern = re.compile(exp, flags=flags).finditer

            text = event.message.message or ''
            matches = list(pattern(text)) or None
            if not matches:
                return
            event.matches = matches

        if self.require_admin:
            text = "`You need to be an admin to use this command!`"
            if not isinstance(event._chat_peer, types.PeerUser):
                is_creator = False
                is_admin = False
                creator = hasattr(event.chat, 'creator')
                admin_rights = hasattr(event.chat, 'admin_rights')
                if not creator and not admin_rights:
                    event.chat = event._client.loop.create_task(
                        event.get_chat()
                    )

                if self.incoming:
                    try:
                        p = event._client.loop.create_task(
                            event._client(
                                functions.channels.GetParticipantRequest(
                                    channel=event.chat_id,
                                    user_id=event.sender_id
                                )
                            )
                        )
                        participant = p.participant
                    except Exception:
                        participant = None
                    if isinstance(
                        participant, types.ChannelParticipantCreator
                    ):
                        is_creator = True
                    if isinstance(participant, types.ChannelParticipantAdmin):
                        is_admin = True
                else:
                    is_creator = event.chat.creator
                    is_admin = event.chat.admin_rights

                if not is_creator:
                    if not is_admin:
                        if self.outgoing and event.message.out:
                            event._client.loop.create_task(
                                event.answer(text)
                            )
                        elif self.incoming and not event.message.out:
                            event._client.loop.create_task(
                                event.answer(text, reply=True)
                            )
                        return
        return event


@events.common.name_inner_event
class MessageEdited(NewMessage):
    """Custom MessageEdited event inheriting the custom NewMessage event"""

    @classmethod
    def build(cls, update, others=None, self_id=None):
        """Required to check if message is edited, double events"""
        if isinstance(update, (types.UpdateEditMessage,
                               types.UpdateEditChannelMessage)):
            return cls.Event(update.message)

    class Event(NewMessage.Event):
        """Overriding the default Event which inherits Telethon's NewMessage"""
        pass  # Required if we want a different name for it
