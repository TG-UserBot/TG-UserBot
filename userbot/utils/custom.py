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


import asyncio
import io
import logging
from typing import List, Tuple, Union

from telethon.extensions import markdown
from telethon.tl import custom, functions, types


LOGGER = logging.getLogger(__name__)
MAXLIM: int = 4096


class Message(custom.Message):
    """Custom message type with the answer bound method"""

    def __init__(self, id, **kwargs):
        for k, v in kwargs.copy().items():
            if k.startswith('_'):
                del kwargs[k]
        super().__init__(id, **kwargs)

    async def answer(
        self,
        *args,
        log: str or Tuple[str, str] = None,
        reply: bool = False,
        **kwargs
    ) -> Union[custom.Message, List[custom.Message]]:
        message = await self._client.get_messages(
            self.chat_id, ids=self.id
        )
        reply_to = self.reply_to_msg_id or self.id

        if len(args) == 1 and isinstance(args[0], str):
            is_reply = reply or kwargs.get('reply_to', False)
            text = args[0]
            msg, msg_entities = markdown.parse(text)
            if len(msg) <= MAXLIM:
                if (
                    is_reply or self.media or self.fwd_from or
                    not (message and message.out)
                ):
                    kwargs.setdefault('reply_to', reply_to)
                    try:
                        msg = await self.respond(text, **kwargs)
                    except Exception as e:
                        LOGGER.exception(e)
                else:
                    if len(msg_entities) > 100:
                        messages = await _resolve_entities(
                            msg, msg_entities
                        )
                        chunks = [markdown.unparse(t, e) for t, e in messages]
                        msg = []
                        try:
                            first_msg = await self.edit(chunks[0], **kwargs)
                        except Exception as e:
                            LOGGER.exception(e)
                        msg.append(first_msg)
                        for t in chunks[1:]:
                            try:
                                sent = await self.respond(t, **kwargs)
                                msg.append(sent)
                            except Exception as e:
                                LOGGER.exception(e)
                    else:
                        try:
                            msg = await self.edit(text, **kwargs)
                        except Exception as e:
                            LOGGER.exception(e)
            else:
                if (
                    message and message.out and
                    not (message.fwd_from or message.media)
                ):
                    await self.edit("`Output exceeded the limit.`")
                kwargs.setdefault('reply_to', reply_to)
                output = io.BytesIO(msg.strip().encode())
                output.name = "output.txt"
                try:
                    msg = await self.respond(
                        file=output,
                        **kwargs
                    )
                    output.close()
                except Exception as e:
                    output.close()
                    LOGGER.exception(e)
        else:
            kwargs.setdefault('reply_to', reply_to)
            try:
                msg = await self.respond(*args, **kwargs)
            except Exception as e:
                LOGGER.exception(e)

        if log:
            if isinstance(log, tuple):
                command, extra = log
                text = f"**USERBOT LOG** #{command}"
                if extra:
                    text += f"\n{extra}"
            else:
                text = f"**USERBOT LOG** `Executed command:` #{log}"
            if self._client.logger:
                logger_group = self._client.config['userbot'].getint(
                    'logger_group_id', False
                )
                entity = False
                try:
                    entity = await self._client.get_input_entity(logger_group)
                except TypeError:
                    LOGGER.info("Your logger group ID is unsupported")
                except ValueError:
                    LOGGER.info("Your logger group ID cannot be found")
                except Exception as e:
                    LOGGER.exception(e)

                if entity:
                    message, msg_entities = markdown.parse(text)
                    if len(message) <= MAXLIM and len(msg_entities) < 100:
                        messages = [(message, msg_entities)]
                    else:
                        messages = await _resolve_entities(
                            message, msg_entities
                        )
                    for text, entities in messages:
                        try:
                            await self._client(
                                functions.messages.SendMessageRequest(
                                    peer=entity,
                                    message=text,
                                    no_webpage=True,
                                    silent=True,
                                    entities=entities
                                )
                            )
                            await asyncio.sleep(2)
                        except Exception as e:
                            print("Report this error to the support group.")
                            LOGGER.exception(e)
        return msg


Message.register(types.Message)
# In-case you want a literal match for is instance
# Message.register(type(types.Message))


async def _resolve_entities(message: str, entities: list) -> dict:
    """Don't even bother trying to figure this mess out"""
    messages = []
    while entities:
        end = 100 if len(entities) >= 100 else len(entities)
        if len(message) > MAXLIM:
            end, _ = min(
                enumerate(entities[:end]),
                key=lambda x: abs(x[1].offset + x[1].length - MAXLIM)
            )
            if end == 0:
                msg_end = entities[0].offset + entities[0].length
                if msg_end > MAXLIM:
                    entity_type = getattr(types, type(entities[0]).__name__)
                    kwargs = vars(entities[0])
                    kwargs.update({'offset': 0})
                    for i in range(0, msg_end, MAXLIM):
                        end = i+MAXLIM if i+MAXLIM <= msg_end else msg_end
                        m_chunk = message[i:end]
                        kwargs.update({'length': len(m_chunk)})
                        messages.append((m_chunk, [entity_type(**kwargs)]))
                else:
                    messages.append((message[:msg_end], [entities[0]]))
                next_offset, _ = await _next_offset(1, entities)
                del entities[0]
                message = message[msg_end:]
                await _reset_entities(entities, msg_end, next_offset)
                continue
            end = end + 1  # We don't want the index

        e_chunk = entities[:end]
        next_offset, last_chunk = await _next_offset(end, entities)
        if last_chunk:
            msg_end = len(message) + 1
        else:
            msg_end = e_chunk[-1].offset + e_chunk[-1].length
        t_chunk = message[:msg_end]
        messages.append((t_chunk, e_chunk))
        entities = entities[end:]
        message = message[len(t_chunk):]
        if entities:
            await _reset_entities(entities, msg_end, next_offset)
    return messages


async def _reset_entities(entities: list, end: int, next_offset: int) -> None:
    """Reset the offset of entities's list which has been cut"""
    offset = entities[0].offset
    increment = 0 if next_offset == end else next_offset - end
    for entity in entities:
        entity.offset = entity.offset + increment - offset


async def _next_offset(end, entities) -> Tuple[int, int]:
    """Find out how much length we need to skip ahead for the next entities"""
    last_chunk = False
    if len(entities) >= end+1:
        next_offset = entities[end].offset
    else:
        # It's always the last entity so just grab the last index
        next_offset = entities[-1].offset + entities[-1].length
        last_chunk = True
    return next_offset, last_chunk
