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
import datetime
import importlib
import inspect
import io
import logging
import re
import typing

from telethon import errors, events
from telethon.extensions import markdown, html
from telethon.tl import custom, functions, types
from telethon.hints import FileLike, MarkupLike, DateLike


LOGGER = logging.getLogger(__name__)
MAXLIM: int = 4096
whitespace_exp: re.Pattern = re.compile(r'^\s')
file_kwargs = (
    'file', 'caption', 'force_document', 'clear_draft', 'progress_callback',
    'attributes', 'thumb', 'allow_cache', 'voice_note', 'video_note',
    'buttons', 'supports_streaming'
)


async def answer(
    self,
    entity,
    message: str or None = '',
    *,
    reply_to: typing.Union[int, types.Message] = None,
    parse_mode: typing.Optional[str] = 'markdown',
    link_preview: bool = False,
    file: typing.Union[FileLike, typing.Sequence[FileLike]] = None,
    force_document: bool = False,
    clear_draft: bool = False,
    buttons: MarkupLike = None,
    silent: bool = True,
    schedule: DateLike = None,
    log: str or typing.Tuple[str, str] = None,
    reply: bool = False,
    self_destruct: int = None,
    event: custom.Message = None
) -> typing.Union[None, custom.Message, typing.Sequence[custom.Message]]:
    """Custom bound method for the Message object"""
    if hasattr(entity, 'get_input_chat'):
        entity = await entity.get_input_chat()
    message_out = None
    kwargs = {
        'parse_mode': parse_mode,
        'link_preview': link_preview,
        'file': file,
        'force_document': force_document,
        'buttons': buttons,
        'schedule': schedule,
    }
    kwargs2 = {
        'reply_to': reply_to,
        'silent': silent,
        'clear_draft': clear_draft,
    }
    start_date = datetime.datetime.now(datetime.timezone.utc)
    reply_to = event.reply_to_msg_id or event.id if reply and event else None
    _reply_to = kwargs2.get('reply_to', None)
    is_outgoing = event.out if event else False
    is_forward = event.fwd_from if event else False
    parser = html if parse_mode in ('html', 'HTML') else markdown
    if event is not None:
        is_media = any([k for k in file_kwargs if getattr(event, k, False)])
    else:
        is_media = any([k for k in file_kwargs if kwargs.get(k, False)])
    if _reply_to and not isinstance(_reply_to, int):
        if isinstance(_reply_to, events.ChatAction.Event):
            action = _reply_to.action_message
            kwargs2['reply_to'] = action.reply_to_msg_id or action.id
    if kwargs2['reply_to'] is None:
        kwargs2['reply_to'] = reply_to

    if message and isinstance(message, str) and not is_media:
        is_reply = reply or kwargs2.get('reply_to', False)
        msg, msg_entities = parser.parse(message)
        if len(msg) <= MAXLIM:
            if is_reply or not is_outgoing or is_forward:
                try:
                    message_out = await self.send_message(
                        entity, message, **kwargs, **kwargs2
                    )
                except Exception as e:
                    raise e
            else:
                if len(msg_entities) > 100:
                    message_out = []
                    messages = await _resolve_entities(msg, msg_entities)
                    chunks = [parser.unparse(t, e) for t, e in messages]
                    try:
                        if event and is_outgoing:
                            first_msg = await self.edit_message(
                                event.chat_id, event.id, chunks[0], **kwargs
                            )
                        else:
                            first_msg = await self.send_message(
                                entity, chunks[0], **kwargs, **kwargs2
                            )
                    except errors.rpcerrorlist.MessageIdInvalidError:
                        first_msg = await self.send_message(
                            entity, chunks[0], **kwargs, **kwargs2
                        )
                    except Exception as e:
                        raise e
                    message_out.append(first_msg)
                    for chunk in chunks[1:]:
                        try:
                            sent = await self.send_message(
                                entity, chunk, **kwargs, **kwargs2
                            )
                            message_out.append(sent)
                        except Exception as e:
                            raise e
                else:
                    try:
                        if event and is_outgoing:
                            message_out = await self.edit_message(
                                event.chat_id, event.id, message, **kwargs
                            )
                        else:
                            message_out = await self.send_message(
                                entity, message, **kwargs, **kwargs2
                            )
                    except errors.rpcerrorlist.MessageIdInvalidError:
                        message_out = await self.send_message(
                            entity, message, **kwargs, **kwargs2
                        )
                    except Exception as e:
                        raise e
        else:
            if event and not is_forward and not is_media and is_outgoing:
                try:
                    await self.edit_message(
                        event.chat_id, event.id,
                        "`Output exceeded the limit.`"
                    )
                except Exception as e:
                    raise e

            output = io.BytesIO(msg.strip().encode())
            output.name = "output.txt"
            kwargs['file'] = output
            try:
                message_out = await self.send_message(
                    entity, **kwargs, **kwargs2
                )
                output.close()
            except Exception as e:
                output.close()
                raise e
    else:
        try:
            if is_outgoing and not kwargs2['reply_to']:
                await event.delete()
            message_out = await self.send_message(
                entity, message, **kwargs, **kwargs2
            )
        except Exception as e:
            raise e

    if message_out is not None:
        if isinstance(message_out, list):
            for message in message_out:
                message.date = start_date
        else:
            message_out.date = start_date

    if (
        self_destruct and
        self.config['userbot'].getboolean('self_destruct_msg', True)
    ):
        asyncio.create_task(_self_destructor(message_out, self_destruct))

    if log:
        if isinstance(log, typing.Tuple):
            command, extra = log
            text = f"**USERBOT LOG** #{command}"
            if extra:
                text += f"\n{extra}"
        else:
            text = f"**USERBOT LOG** `Executed command:` #{log}"
        if self.logger:
            message, msg_entities = await self._parse_message_text(
                text, kwargs.get('parse_mode')
            )
            if len(message) <= MAXLIM and len(msg_entities) < 100:
                messages = [(message, msg_entities)]
            else:
                messages = await _resolve_entities(message, msg_entities)
            for text, entities in messages:
                try:
                    await self(
                        functions.messages.SendMessageRequest(
                            peer=self.logger,
                            message=text,
                            no_webpage=True,
                            silent=True,
                            entities=entities
                        )
                    )
                    await asyncio.sleep(2)
                except Exception as e:
                    LOGGER.error("Report this error to the support group.")
                    raise e
    return message_out


async def resanswer(
    self,
    entity,
    message: str,
    plugin: str = None, name: str = None, formats: dict = {},
    **kwargs
) -> custom.Message or None:
    if hasattr(entity, 'get_input_chat'):
        entity = await entity.get_input_chat()
    sent = None
    chat_id = entity

    if not (plugin and name):
        return await self.answer(
            entity, message.format(**formats), **kwargs
        )

    try:
        mod = importlib.import_module('.' + plugin, package='resources')
    except (ImportError, ModuleNotFoundError):
        return await self.answer(
            entity, message.format(**formats), **kwargs
        )

    if not hasattr(mod, name):
        sent = await self.answer(
            entity, message.format(**formats), **kwargs
        )

    strings = getattr(mod, name, [])
    estrings = getattr(mod, name + '_extra', [])
    strings = await resolve_strings(strings)
    estrings = await resolve_strings(estrings)

    try:
        text = strings[0] if len(strings) >= 1 else None
        if text is not None:
            sent = await self.answer(
                entity, text.format(**formats), **kwargs
            )
    except KeyError:
        LOGGER.error(
            'Invalid string %s found in %s resource', name, plugin
        )
        sent = await self.answer(
            entity, message.format(**formats), **kwargs
        )

    # Wouldn't want to reply to a random message in a different groupchat
    kwargs.pop('reply_to', None)
    kwargs.pop('reply', None)
    # Only use a different chat_id for extra messages
    chat_id = getattr(mod, 'chat_id', chat_id)
    if isinstance(chat_id, str) and chat_id.isdigit():
        chat_id = int(chat_id)
    if not isinstance(chat_id, list):
        chat_id = [chat_id]

    for string in estrings:
        try:
            for chat in chat_id:
                await self.send_message(
                    chat, string.format(**formats), **kwargs
                )
        except KeyError:
            LOGGER.warning(
                'Invalid extra string %s found in %s resource', name, plugin
            )
    return sent


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
                    kwargs.update(offset=0)
                    for i in range(0, msg_end, MAXLIM):
                        end = i+MAXLIM if i+MAXLIM <= msg_end else msg_end
                        m_chunk = message[i:end]
                        kwargs.update(length=len(m_chunk))
                        messages.append((m_chunk, [entity_type(**kwargs)]))
                else:
                    messages.append((message[:msg_end], [entities[0]]))
                next_offset, _ = await _next_offset(1, entities)
                del entities[0]
                message = message[msg_end:]
                await _reset_entities(entities, msg_end, next_offset)
                continue
            end = end + 1  # We don't want the index

        _, last_chunk = await _next_offset(end, entities)
        if not last_chunk:
            last_end = entities[end].offset + entities[end].length
            if end > 3 and not whitespace_exp.search(message[last_end:]):
                for e in entities[:end:-1]:
                    start = e.offset + e.length
                    if end == 2 or whitespace_exp.search(message[start:]):
                        break
                    end = end - 1
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


async def _next_offset(end, entities) -> typing.Tuple[int, bool]:
    """Find out how much length we need to skip ahead for the next entities"""
    last_chunk = False
    if len(entities) >= end+1:
        next_offset = entities[end].offset
    else:
        # It's always the last entity so just grab the last index
        next_offset = entities[-1].offset + entities[-1].length
        last_chunk = True
    return next_offset, last_chunk


async def _self_destructor(
    event: typing.Union[custom.Message, typing.Sequence[custom.Message]],
    timeout: int or float
) -> typing.Union[custom.Message, typing.Sequence[custom.Message]]:
    await asyncio.sleep(timeout)
    if isinstance(event, list):
        deleted = []
        for e in event:
            deleted.append(await e.delete())
    else:
        deleted = await event.delete()
    return deleted


async def resolve_strings(strings: str or None or list) -> list:
    tmp = []
    if inspect.isfunction(strings):
        strings = strings()

    if isinstance(strings, list):
        tmp = [
            str(s()) if inspect.isfunction(s) else str(s)
            for s in strings if s is not None
        ]
    elif strings is not None:
        tmp = [str(strings)]
    return tmp
