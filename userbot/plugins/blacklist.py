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


import dill
import re
from typing import Dict, List, Tuple, Union

from telethon.events import ChatAction
from telethon.tl import types, functions
from telethon.utils import get_display_name, resolve_invite_link

from userbot import client, LOGGER
from userbot.utils.events import NewMessage
from userbot.plugins.plugins_data import Blacklist, GlobalBlacklist


plugin_category = "blacklisting"
redis = client.database

blacklisted_text = (
    "**Automatically banned** {} **because they're{}blacklisted!.**"
)
bio_text = "{} **has been banned due to a{}blacklisted bio match.**"
str_text = "{} **has been banned due to a{}blacklisted string match.**"
url_str = "{} **has been banned due to a{}blacklisted URL match.**"
id_str = "{} **has been banned due to a{}blacklisted ID match.**"

bl_pattern = (
    r"(?P<global>g(?:lobal)?)?"
    r"b(?:lack)?l(?:ist)?"
    r"(?: |$|\n)(?P<match>[\s\S]*)"
)
dbl_pattern = (
    r"r(?:e)?m(?:ove)?"
    r"(?P<global>g(?:lobal)?)?"
    r"b(?:lack)?l(?:ist)?"
    r"(?: |$|\n)(?P<match>[\s\S]*)"
)
wl_pattern = (
    r"w(?:hite)?l(?:ist)?"
    r"(?: |$|\n)(?P<match>[\s\S]*)"
)
dwl_pattern = (
    r"r(?:e)?m(?:ove)?"
    r"w(?:hite)?l(?:ist)?"
    r"(?: |$|\n)(?P<match>[\s\S]*)"
)
dbld_pattern = (
    r"(?:remove|un)"
    r"b(?:lack)?l(?:ist)?"
    r"(?: |$|\n)(?P<match>[\s\S]*)"
)
bls_pattern = (
    r"(?P<global>g(?:lobal)?)?"
    r"b(?:lack)?l(?:ist)?s"
    r"(?: |$|\n)"
    r"(?:(?P<match>[\s\S]*))?"
)
wls_pattern = (
    r"w(?:hite)?l(?:ist)?s"
    r"(?: |$|\n)"
    r"(?:(?P<match>[\s\S]*))?"
)
bld_pattern = (
    r"blacklisted"
    r"(?: |$|\n)"
    r"(?:(?P<match>[\s\S]*))?"
)
id_pattern = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?(?:t\.me\/)?@?(?P<e>\w{5,35}|-?\d{6,16})\/?'
)
invite_pattern = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?t\.me\/(?P<hash>\w{22})\/?'
)
acceptable_options = {
    'id': 'tgid',
    'bio': 'bio',
    'string': 'txt',
    'str': 'txt',
    'domian': 'url',
    'url': 'url'
}
full_key_names = {
    'tgid': '[Telegram IDs]',
    'bio': '[User Bios]',
    'txt': '[Strings]',
    'url': '[URLs]'
}

temp_banlist: List[int] = []
localBlacklists: Dict[int, Blacklist] = {}
blacklistedUsers: Dict[int, Tuple[str, Union[str, int]]] = {}
whitelistedUsers: List[int] = []
whitelistedChats: List[int] = []

if redis:
    local_keys = redis.keys('blacklists:-*')
    if redis.exists('blacklists:global'):
        globalData = dill.loads(redis.get('blacklists:global'))
    else:
        globalData = {}
    for key in local_keys:
        data = dill.loads(redis.get(key))
        localBlacklists[int(key[11:])] = Blacklist(
            bio=data.get('bio', None),
            url=data.get('url', None),
            tgid=data.get('tgid', None),
            txt=data.get('txt', None)
        )
    for option, value in globalData.items():
        setattr(GlobalBlacklist, option, value)
    if redis.exists('blacklist:users'):
        blacklistedUsers = dill.loads(redis.get('blacklist:users'))
    if redis.exists('whitelist:users'):
        whitelistedUsers = dill.loads(redis.get('whitelist:users'))
    if redis.exists('whitelist:chats'):
        whitelistedChats = dill.loads(redis.get('whitelist:chats'))


async def append(
    key: str or bytes, option: str, values: List[Union[str, int]]
) -> Tuple[list, list]:
    """Create/Append values to keys in Redis DB"""
    added = []
    skipped = []

    if redis.exists(key):
        data = dill.loads(redis.get(key))
        if option in data:
            for value in values:
                if value in data[option]:
                    skipped.append(value)
                    continue  # The value is already stored in the DB
                else:
                    data[option].append(value)
                    added.append(value)
        else:
            data.setdefault(option, []).extend(values)
            added.extend(values)
        data = dill.dumps(data)
    else:
        data = dill.dumps({option: values})
    redis.set(key, data)

    key = key[11:]
    blkey = key if key.isalpha() else int(key)
    if added:
        if blkey == 'global':
            gval = getattr(GlobalBlacklist, option, None)
            if gval:
                gval.extend(added)
            else:
                gval = added
            setattr(GlobalBlacklist, option, gval)
        else:
            if blkey in localBlacklists:
                lval = getattr(localBlacklists[blkey], option, None)
                if lval:
                    lval.extend(added)
                else:
                    lval = added
                setattr(localBlacklists[blkey], option, lval)
            else:
                localBlacklists[blkey] = Blacklist(**{option: added})

    return added, skipped


async def unappend(
    key: str or bytes, option: str, values: List[Union[str, int]]
) -> Tuple[list, list]:
    """Remove/Unappend values to keys from Redis DB"""
    removed = []
    skipped = []
    empty = False
    if redis.exists(key):
        data = dill.loads(redis.get(key))
        if option in data:
            for value in values:
                if value in data[option]:
                    data[option].remove(value)
                    removed.append(value)
                else:
                    skipped.append(value)
            for x, y in data.copy().items():
                if len(y) == 0:
                    del data[x]
            if len(data) == 0:
                empty = True
            else:
                data = dill.dumps(data)
        else:
            return removed, skipped
    else:
        return removed, skipped

    if empty:
        redis.delete(key)
    else:
        redis.set(key, data)

    key = key[11:]
    blkey = key if key.isalpha() else int(key)
    if removed:
        if blkey == 'global':
            gval = getattr(GlobalBlacklist, option, None)
            if gval:
                for value in removed:
                    if value in gval:
                        gval.remove(value)
                if gval:
                    setattr(GlobalBlacklist, option, gval)
                else:
                    setattr(GlobalBlacklist, option, None)
        else:
            if blkey in localBlacklists:
                lval = getattr(localBlacklists[blkey], option, None)
                if lval:
                    for value in removed:
                        if value in lval:
                            lval.remove(value)
                    if lval:
                        setattr(localBlacklists[blkey], option, lval)
                    else:
                        setattr(localBlacklists[blkey], option, None)

    return removed, skipped


@client.onMessage(
    command=("blacklist", plugin_category),
    outgoing=True, regex=bl_pattern
)
async def blacklister(event: NewMessage.Event) -> None:
    """Add a blacklisted item in the Redis DB"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    glb = event.matches[0].group('global')
    match = event.matches[0].group('match')
    key = "global" if glb else str(event.chat_id)
    added_values = {}
    skipped_values = {}

    if not match:
        await event.answer(
            '__.(g)bl <value1> .. <valuen> or <option>:<value>__\n'
            '`Available options:` __id, bio, string/str, domain/url__'
        )
        return

    args, kwargs = await client.parse_arguments(match)
    parsed = await get_values(args, kwargs)
    reason = kwargs.get('reason', False)

    if not glb:
        chat = await event.get_chat()
        if not chat.creator:
            if not getattr(chat.admin_rights, 'ban_users', False):
                await event.edit(
                    "`You need to have ban rights to set a blacklist in here.`"
                )
                return

    for option, values in parsed.items():
        if values:
            added, failed = await append("blacklists:" + key, option, values)
            if added:
                added_values.update({option: added})
            if failed:
                skipped_values.update({option: failed})

    if added_values:
        text = f"**New blacklists for {key}:**\n"
        text += await values_to_str(added_values)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.answer(text, log=('blacklist', text))
    if skipped_values:
        text = f"**Skipped blacklists for {key}:**\n"
        text += await values_to_str(skipped_values)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("rmblacklist", plugin_category),
    outgoing=True, regex=dbl_pattern
)
async def unblacklister(event: NewMessage.Event) -> None:
    """Remove a blacklisted item from the dict stored on Redis"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    glb = event.matches[0].group('global')
    match = event.matches[0].group('match')
    key = "global" if glb else str(event.chat_id)
    removed_values = {}
    skipped_values = {}

    if not match:
        await event.answer(
            '__.rm(g)bl <value1> .. <valuen> or <option>:<value>__\n'
            '`Available options:` __id, bio, string/str, domain/url__'
        )
        return

    args, kwargs = await client.parse_arguments(match)
    parsed = await get_values(args, kwargs)
    reason = kwargs.get('reason', None)

    for option, values in parsed.items():
        if values:
            removed, skipped = await unappend(
                "blacklists:" + key, option, values
            )
            if removed:
                removed_values.update({option: removed})
            if skipped:
                skipped_values.update({option: skipped})

    if removed_values:
        text = f"**Removed blacklists for {key}:**\n"
        text += await values_to_str(removed_values)
        if reason:
            text += f"\n`Reason:` `{reason}`"
        await event.answer(text, log=('blacklist', text))
    if skipped_values:
        text = f"**Skipped blacklists for {key}:**\n"
        text += await values_to_str(skipped_values)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("whitelist", plugin_category),
    outgoing=True, regex=wl_pattern
)
async def whitelister(event: NewMessage.Event) -> None:
    """Add a whitelisted user or chat in the Redis DB"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    match = event.matches[0].group('match') or ''
    users = []
    chats = []
    skipped = []
    text = ''
    log = ''

    if match:
        args, _ = await client.parse_arguments(match)
        for user in args:
            if user in whitelistedUsers + whitelistedChats:
                skipped.append(f"`{user}`")
                continue
            try:
                entity = await client.get_entity(user)
                if isinstance(entity, types.User):
                    if not entity.is_self:
                        users.append(entity)
                else:
                    chats.append(entity)
            except Exception:
                skipped.append(f"`{user}`")
    else:
        if event.reply_to_msg_id:
            wl = (await event.get_reply_message()).from_id
            users.append(await client.get_entity(wl))
        else:
            entity = await event.get_chat()
            if event.is_private:
                users.append(entity)
            else:
                chats.append(entity)

    if users:
        usertext = ''
        count = 0
        for user in users:
            entity = await client.get_peer_id(user)
            name = get_display_name(user)
            name = f"[{name}](tg://user?id={entity})"
            if entity not in whitelistedUsers:
                whitelistedUsers.append(entity)
                usertext += f"  {name}"
                count = 1
            else:
                skipped.append(name)
        if count != 0:
            redis.set('whitelist:users', dill.dumps(whitelistedUsers))
            text += "**Whitelisted users:**\n" + usertext
            log += text
            await event.answer(text, log=None if chats else ("whitelist", log))
    if chats:
        chattext = ''
        count = 0
        for chat in chats:
            if chat.username:
                name = f"[{chat.title}](tg://resolve?domain={chat.username})"
            else:
                name = f"`{chat.id}`"
            entity = await client.get_peer_id(chat)
            if entity not in whitelistedChats:
                whitelistedChats.append(entity)
                chattext += f"  {name}"
                count = 1
            else:
                skipped.append(name)
        if count:
            if text:
                text += "\n\n**Whitelisted chats:**\n" + chattext
            else:
                text += "**Whitelisted chats:**\n" + chattext
            redis.set('whitelist:chats', dill.dumps(whitelistedChats))
            log += text
            await event.answer(text, log=("whitelist", log))
    if skipped:
        text = "**Skipped entities:**\n" + ", ".join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("rmwhitelist", plugin_category),
    outgoing=True, regex=dwl_pattern
)
async def unwhitelister(event: NewMessage.Event) -> None:
    """Remove a whitelisted id from the dict stored on Redis"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    match = event.matches[0].group('match') or ''
    users = []
    chats = []
    skipped = []
    text = ''
    log = ''

    if match:
        args, _ = await client.parse_arguments(match)
        for user in args:
            if user in whitelistedUsers:
                users.append(user)
                continue
            elif user in whitelistedChats:
                chats.append(user)
                continue
            try:
                entity = await client.get_entity(user)
                if isinstance(entity, types.User):
                    if not entity.is_self:
                        users.append(entity.id)
                else:
                    chats.append(entity.id)
            except Exception:
                skipped.append(f"`{user}`")
    else:
        if event.reply_to_msg_id:
            entity = (await event.get_reply_message()).from_id
            users.append(await client.get_peer_id(entity))
        else:
            entity = await event.get_chat()
            entity = await client.get_peer_id(entity)
            if event.is_private:
                users.append(entity)
            else:
                chats.append(entity)

    if users and whitelistedUsers:
        count = 0
        usertext = ''
        for user in users:
            if user in whitelistedUsers:
                whitelistedUsers.remove(user)
                usertext += f" `{user}`"
                count = 1
            else:
                skipped.append(f"`{user}`")
        if count:
            if whitelistedUsers:
                redis.set('whitelist:users', dill.dumps(whitelistedUsers))
            else:
                redis.delete('whitelist:users')
            text += "**Un-whitelisted users:**\n" + usertext
            log += text
            await event.answer(
                text, log=None if chats else ("whitelist", text)
            )
    if chats and whitelistedChats:
        count = 0
        chattext = ''
        for chat in chats:
            if chat in whitelistedChats:
                whitelistedChats.remove(chat)
                chattext += f" `{chat}`"
                count = 1
            else:
                skipped.append(f"`{chat}`")
        if count:
            if whitelistedChats:
                redis.set('whitelist:chats', dill.dumps(whitelistedChats))
            else:
                redis.delete('whitelist:chats')
            if text:
                text += "**\n\nUn-whitelisted chats:**\n" + chattext
            else:
                text += "**Un-whitelisted chats:**\n" + chattext
            log += text
            await event.answer(text, log=("whitelist", text))
    if skipped:
        text = "**Skipped entities:**\n" + ", ".join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("unblacklist", plugin_category),
    outgoing=True, regex=dbld_pattern
)
async def unblacklistuser(event: NewMessage.Event) -> None:
    """Unblacklist a user."""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    match = event.matches[0].group('match') or ''
    users = []
    skipped = []

    if match:
        args, _ = await client.parse_arguments(match)
        for user in args:
            if user in blacklistedUsers:
                users.append(user)
                continue
            try:
                entity = await client.get_entity(user)
                if isinstance(entity, types.User):
                    if not entity.is_self:
                        users.append(entity.id)
                else:
                    skipped.append(f"`{user}`")
            except Exception:
                skipped.append(f"`{user}`")
    else:
        if event.reply_to_msg_id:
            entity = (await event.get_reply_message()).from_id
            users.append(await client.get_peer_id(entity))
        else:
            entity = await event.get_chat()
            entity = await client.get_peer_id(entity)
            if event.is_private:
                users.append(entity)

    if users and blacklistedUsers:
        text = "**Un-blacklisted users:**\n"
        targets = []
        for user in users:
            if user in blacklistedUsers:
                blacklistedUsers.pop(user)
                targets.append(f"[{user}](tg://user?id={user})")
        if blacklistedUsers:
            redis.set('blacklist:users', dill.dumps(blacklistedUsers))
        else:
            redis.delete('blacklist:users')
        text += ", ".join(targets)
        await event.answer(text, log=('unblacklist', text))
    if skipped:
        text = "**Skipped users:**\n"
        text += ', '.join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(
    command=("blacklists", plugin_category),
    outgoing=True, regex=bls_pattern
)
async def listbls(event: NewMessage.Event) -> None:
    """Get a list of all the (global) blacklists"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    glb = event.matches[0].group('global')
    match = event.matches[0].group('match') or ''
    args, kwargs = await client.parse_arguments(match)
    parsed = await get_values(None, kwargs)

    if match:
        blacklisted = []
        not_blacklisted = []
        for option, values in parsed.items():
            if values:
                if glb:
                    attr = getattr(GlobalBlacklist, option, None)
                    if attr:
                        for v in values:
                            if v in attr:
                                blacklisted.append(v)
                            else:
                                not_blacklisted.append(v)
                else:
                    if event.chat_id not in localBlacklists:
                        break
                    attr = getattr(
                        localBlacklists[event.chat_id], option, None
                    )
                    if attr:
                        for v in values:
                            if v in attr:
                                blacklisted.append(v)
                            else:
                                not_blacklisted.append(v)
        if blacklisted:
            text = "**Already blacklisted values:**\n"
            text += ', '.join(f'`{b}`' for b in blacklisted)
            await event.answer(text, reply=True)
        if not_blacklisted:
            text = "**Not blacklisted values:**\n"
            text += ', '.join(f'`{b}`' for b in not_blacklisted)
            await event.answer(text, reply=True)
        if args and len(args) == 1:
            text = None
            arg = args[0].lower()
            if glb:
                attr = getattr(GlobalBlacklist, arg, None)
                if attr:
                    values = ', '.join(attr)
                    text = f"**GLobal {arg} blacklists:**\n```{values}```"
                else:
                    text = f"__There are no global {arg} blacklists.__"
            else:
                attr = getattr(localBlacklists[event.chat_id], option, None)
                if attr:
                    values = ', '.join(attr)
                    text = f"**{arg.title()} blacklists:**\n```{values}```"
                else:
                    text = f"__There are no {arg} blacklists.__"
            if text:
                await event.answer(text)
    else:
        if glb:
            gbls = await blattributes(GlobalBlacklist)
            if gbls:
                text = f"**Global blacklists:**\n{gbls}"
            else:
                text = f"__There are no global blacklists.__"
        else:
            if event.chat_id not in localBlacklists:
                await event.answer('__There are no blacklists set here.__')
                return
            bls = await blattributes(localBlacklists[event.chat_id])
            if bls:
                text = f"**Blacklists:**\n{bls}"
            else:
                text = f"__There are no blacklists.__"
        await event.answer(text)


@client.onMessage(
    command=("whitelists", plugin_category),
    outgoing=True, regex=wls_pattern
)
async def listwls(event: NewMessage.Event) -> None:
    """Get a list of all the whitelists"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    match = event.matches[0].group('match') or ''
    args, kwargs = await client.parse_arguments(match)
    option = args[0] if args else None
    user = kwargs.get('user', None)
    chat = kwargs.get('chat', None)

    if option and option.lower() not in ['users', 'chats', 'user', 'chat']:
        await event.answer(
            "`Invalid argument. Available options:`\n"
            "__user(s) or chat(s)__\n"
            "ex: `.wls user=<123>` or `.wls chat=<456>`"
        )
        return

    if option:
        if option in ['user', 'users']:
            if whitelistedUsers:
                text = "**Whitelisted users:**\n"
                text += ', '.join([f'`{x}`' for x in whitelistedUsers])
            else:
                text = "__There are no whitelisted users.__"
        else:
            if whitelistedChats:
                text = "**Whitelisted chats:**\n"
                text += ', '.join([f'`{x}`' for x in whitelistedChats])
            else:
                text = "__There are no whitelisted chats.__"
    else:
        if not whitelistedChats and not whitelistedUsers:
            text = "__There are no whitelisted users or chats.__"
            await event.answer(text)
            return
        if user or chat:
            text = ''
            if user:
                if isinstance(user, str):
                    user = await get_peer_id(user)
                elif isinstance(user, list):
                    user = user[0]
                    if isinstance(user, str):
                        user = await get_peer_id(user)
                if user in whitelistedUsers:
                    text += f"`{user} is already whitelisted!`"
                else:
                    text += f"`{user} is not whitelisted!`"
            if chat:
                if isinstance(chat, str):
                    user = await get_peer_id(chat)
                elif isinstance(chat, list):
                    chat = chat[0]
                    if isinstance(chat, str):
                        chat = await get_peer_id(chat)
                if text:
                    text += "\n\n"
                if chat in whitelistedChats:
                    text += f"`{chat} is already whitelisted!`"
                else:
                    text += f"`{chat} is not whitelisted!`"
            await event.answer(text)
        else:
            text = ""
            if whitelistedUsers:
                text += "**Whitelisted users:**\n"
                text += ', '.join([f'`{x}`' for x in whitelistedUsers])
            if whitelistedChats:
                text += "\n**Whitelisted chats:**\n"
                text += ', '.join([f'`{x}`' for x in whitelistedChats])
            if text:
                await event.answer(text)


@client.onMessage(
    command=("blacklisted", plugin_category),
    outgoing=True, regex=bld_pattern
)
async def listbld(event: NewMessage.Event) -> None:
    """Get a list of all the blacklisted users"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    match = event.matches[0].group('match') or ''
    users = []
    skipped = []
    args, _ = await client.parse_arguments(match)
    option = args[0] if len(args) == 1 and isinstance(args[0], str) else None

    if option and option.lower() not in ['txt', 'tgid', 'url']:
        await event.answer(
            "`Invalid argument. Available options:`\n"
            "__txt or tgid or url__"
        )
        return

    if option and blacklistedUsers:
        option = option.lower()
        matches = {}
        for user, ban in blacklistedUsers.items():
            ban_type, match = ban
            if ban_type == option:
                matches.update({user: match})

        if matches:
            text = "**Blacklisted users:**\n"
            text += ',\n'.join([
                f'[{user}](tg://user?id={user}): `{x}`, `{y}`'
                for x, y in blacklistedUsers.items()
            ])
        else:
            text = f"__There are no {option} blacklisted users.__"
    elif args and blacklistedUsers:
        text = "**Blacklisted users:**\n"
        for user in args:
            if user in blacklistedUsers:
                t, v = blacklistedUsers[user]
                users.append(
                    f'[{user}](tg://user?id={user}): `{t}`, `{v}`'
                )
                continue
            try:
                entity = await client.get_entity(user)
                if isinstance(entity, types.User):
                    if not entity.is_self:
                        if user in blacklistedUsers:
                            t, v = blacklistedUsers[entity.id]
                            users.append(
                                f'[{user}](tg://user?id={user}): `{t}`, `{v}`'
                            )
                        else:
                            skipped.append(f"`{entity.id}`")
                else:
                    skipped.append(f"`{entity.id}`")
            except Exception:
                skipped.append(f"`{user}`")
        text += ',\n'.join(users)
    else:
        if not blacklistedUsers:
            text = "__There are no blacklisted users.__"
        else:
            text = "**Blacklisted users:**\n"
            text += ', '.join([
                f'[{user}](tg://user?id={x})' for x in blacklistedUsers
            ])

    await event.answer(text)
    if skipped:
        text = "**Skipped users:**\n"
        text += ', '.join(skipped)
        await event.answer(text, reply=True)


@client.onMessage(incoming=True)
async def inc_listener(event: NewMessage.Event) -> None:
    """Filter incoming messages for blacklisting."""
    broadcast = getattr(event.chat, 'broadcast', False)
    if not redis or event.is_private or broadcast:
        return
    if (
        event.chat_id in whitelistedChats or
        event.from_id in whitelistedUsers or
        await is_admin(event.chat_id, event.sender_id)
    ):
        return
    elif event.from_id in blacklistedUsers:
        if event.from_id not in temp_banlist:
            await ban_user(event, blacklisted_text)
        return

    invite = False
    invite_match = invite_pattern.search(event.text)
    tgid_check = False
    localbl = localBlacklists.get(event.chat_id, False)

    if invite_match:
        _, invite, _ = resolve_invite_link(invite_match.group('hash'))
        try:
            invite = await client.get_peer_id(invite, False)
        except Exception as e:
            LOGGER.debug(e)

    if GlobalBlacklist.txt:
        for value in GlobalBlacklist.txt:
            string = await escape_string(value)
            if re.search(string, event.text, flags=re.I):
                if await ban_user(event, str_text, 'txt', value, True):
                    return
                break
    elif localbl and getattr(localbl, 'txt', False):
        for value in localBlacklists[event.chat_id].txt:
            string = await escape_string(value)
            if re.search(string, event.text, flags=re.I):
                if await ban_user(event, str_text, 'txt', value):
                    return
                break

    if GlobalBlacklist.url:
        for value in GlobalBlacklist.url:
            string = re.sub(r'(?<!\\)\*', r'\\w+', value, count=0)
            if re.search(string, event.text, flags=re.I):
                if await ban_user(event, url_str, 'url', value, True):
                    return
                break
    elif localbl and getattr(localbl, 'url', False):
        for value in localBlacklists[event.chat_id].url:
            string = re.sub(r'(?<!\\)\*', r'\\w+', value, count=0)
            if re.search(string, event.text, flags=re.I):
                if await ban_user(event, url_str, 'url', value):
                    return
                break

    if GlobalBlacklist.tgid or (localbl and hasattr(localbl, 'tgid')):
        tgid_check = True

    if tgid_check:
        globalid = getattr(GlobalBlacklist, 'tgid', []) or []
        localid = getattr(localbl, 'tgid', []) or []
        if event.sender_id in globalid:
            if await ban_user(event, id_str, 'tgid', value.sender_id, True):
                return
        elif event.sender_id in localid:
            if await ban_user(event, id_str, 'tgid', value.sender_id):
                return
        entities = getattr(event, 'entities', None) or []
        for entity in entities:
            if (
                isinstance(
                    entity,
                    (types.MessageEntityMention, types.MessageEntityUrl)
                )
            ):
                entity = id_pattern.search(
                    event.text[entity.offset:entity.offset+entity.length]
                )
                entity = entity.group('e') if entity else entity
                value = await client.get_peer_id(entity) if entity else 0
            elif isinstance(entity, types.MessageEntityMentionName):
                value = await client.get_peer_id(entity.user_id)
            else:
                value = None

            if value and invite:
                temp = await client.get_peer_id(value, False)
                if invite == temp:
                    if await ban_user(event, id_str, 'tgid', value):
                        return
                    break

            if value in globalid:
                if await ban_user(event, id_str, 'tgid', value, True):
                    return
                break
            elif localbl and hasattr(localbl, 'tgid'):
                if value in localBlacklists[event.chat_id].tgid:
                    if await ban_user(event, id_str, 'tgid', value):
                        return
                    break


@client.on(ChatAction)
async def bio_filter(event: ChatAction.Event) -> None:
    """Filter incoming messages for blacklisting."""
    match = False
    broadcast = getattr(event.chat, 'broadcast', False)

    if not redis or event.is_private or broadcast:
        return

    if event.user_added or event.user_joined:
        try:
            sender = await event.get_input_user()
            chat = await event.get_chat()
            sender_id = await client.get_peer_id(sender)
            chat_id = await client.get_peer_id(chat)
            localbl = localBlacklists.get(chat_id, False)
        except (ValueError, TypeError):
            return
        if (
            chat_id in whitelistedChats or
            sender_id in whitelistedUsers or
            await is_admin(chat_id, sender_id)
        ):
            return
        elif sender_id in blacklistedUsers:
            if sender_id not in temp_banlist:
                await ban_user(event, blacklisted_text)
            return
        elif GlobalBlacklist.tgid and sender_id in GlobalBlacklist.tgid:
            if await ban_user(event, id_str, 'bio', match, True):
                return
        elif localbl and localbl.tgid and sender_id in localbl.tgid:
            if await ban_user(event, id_str, 'bio', match):
                return

        user = await client(functions.users.GetFullUserRequest(id=sender))
        if GlobalBlacklist.bio:
            for value in GlobalBlacklist.bio:
                bio = await escape_string(value)
                if re.search(bio, user.about, flags=re.I):
                    match = value
                    break
        elif localbl and hasattr(localbl, 'bio'):
            for value in localBlacklists[chat_id].bio:
                bio = await escape_string(value)
                if re.search(bio, user.about, flags=re.I):
                    match = value
                    break

        if match:
            await ban_user(event, bio_text.format(match), 'bio', match)


async def escape_string(string: str) -> str:
    """Literal match everything but * and ?"""
    string = re.sub(r'(?<!\\)\*', '.+', string, count=0)
    string = re.sub(r'(?<!\\)\?', '.', string, count=0)
    return string


async def is_admin(chat_id, sender_id) -> bool:
    """Check if the sender is an admin or bot"""
    try:
        result = await client(functions.channels.GetParticipantRequest(
            channel=chat_id,
            user_id=sender_id
        ))
        if isinstance(
            result.participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator)
        ):
            return True
    except Exception:
        return False


async def ban_user(
    event: NewMessage.Event or ChatAction.Event, text: str,
    bl_type: str = None, match: Union[str, int] = None, globally: bool = False
) -> bool:
    if isinstance(event, NewMessage.Event):
        sender = await event.get_input_sender()
    else:
        sender = await event.get_input_user()
    temp_banlist.append(sender)
    chat = await event.get_chat()
    ban_right = getattr(chat.admin_rights, 'ban_users', False)
    delete_messages = getattr(chat.admin_rights, 'delete_messages', False)
    if not (ban_right or chat.creator):
        return False
    user_href = "[{0}](tg://user?id={0})".format(sender.user_id)
    try:
        await client.edit_permissions(
            entity=chat.id,
            user=sender,
            view_messages=False
        )
        if delete_messages:
            await event.delete()
        text = text.format(user_href, ' globally ' if globally else ' ')
        await event.respond(text)
        if client.logger:
            logger_group = client.config['userbot'].getint(
                'logger_group_id', 'me'
            )
            if chat.username:
                chat_href = (
                    f"[{chat.title}]"
                    f"(tg://resolve?domain={chat.username})"
                )
            else:
                chat_href = f"[{chat.title}] `{chat.id}`"
            log_text = (
                "**USERBOT LOG** #blacklist\n"
                f"Banned {user_href} from {chat_href}.\n"
            )
            if bl_type and match:
                log_text += f"Blacklist type: `{bl_type}`.\nMatch: `{match}`"
            await client.send_message(logger_group, log_text)
        if bl_type and match and sender.user_id not in blacklistedUsers:
            blacklistedUsers.update({sender.user_id: (bl_type, match)})
            redis.set('blacklist:users', dill.dumps(blacklistedUsers))
        return True
    except Exception as e:
        exc = await client.get_traceback(e)
        await event.respond(f"**Couldn't ban user. Exception:\n**```{exc}```")
        LOGGER.exception(e)
        return False
    finally:
        temp_banlist.remove(sender)


async def blattributes(blacklist) -> str:
    """Get all the available attributes from a BL class"""
    text = ""
    strings = getattr(blacklist, 'txt', None)
    bio = getattr(blacklist, 'bio', None)
    tgid = getattr(blacklist, 'tgid', None)
    url = getattr(blacklist, 'url', None)
    if strings:
        text += f"\n**{full_key_names['txt']}:** "
        text += ', '.join([f'`{x}`' for x in strings])
    if bio:
        text += f"\n\n**{full_key_names['bio']}:** "
        text += ', '.join([f'`{x}`' for x in bio])
    if tgid:
        text += f"\n\n**{full_key_names['tgid']}:** "
        text += ', '.join([f'`{x}`' for x in tgid])
    if url:
        text += f"\n\n**{full_key_names['url']}:** "
        text += ', '.join([f'`{x}`' for x in url])
    return text


async def get_values(args: list, kwargs: dict) -> Dict[str, List]:
    """
        Iter through the parsed arguments and
        return a list of the proper options.
    """
    txt: List[str] = []
    tgid: List[int] = []
    bio: List[str] = []
    url: List[str] = []

    if args:
        for i in args:
            if isinstance(i, list):
                txt += [str(o) for o in i if o not in txt]
            else:
                if i not in txt:
                    txt.append(str(i))

    temp_id = kwargs.get('id', [])
    await append_args_to_list(tgid, temp_id, True)

    temp_bio = kwargs.get('bio', [])
    await append_args_to_list(bio, temp_bio)

    temp_string = kwargs.get('string', [])
    temp_str = kwargs.get('str', [])
    if isinstance(temp_str, list):
        temp_string.extend(temp_str)
    else:
        temp_string.append(temp_str)
    await append_args_to_list(txt, temp_string)

    temp_domain = kwargs.get('domain', [])
    temp_url = kwargs.get('url', [])
    if isinstance(temp_url, list):
        temp_domain.extend(temp_url)
    else:
        temp_domain.append(temp_url)
    await append_args_to_list(url, temp_domain)

    return {'txt': txt, 'tgid': tgid, 'bio': bio, 'url': url}


async def append_args_to_list(
    option: list, args_list: str or list, tg_id: bool = False
) -> list:
    """Iter through the values and append if they're not in the list."""
    if isinstance(args_list, list):
        for i in args_list:
            if tg_id:
                value = await get_peer_id(i)
                if value and value not in option:
                    option.append(value)
            else:
                i = str(i)
                if i not in option:
                    option.append(i)
    else:
        if tg_id:
            i = await get_peer_id(args_list)
            if i and i not in option:
                option.append(i)
        else:
            i = str(i)
            if i not in option:
                option.append(i)

    return option


async def get_peer_id(entity: str or int) -> int:
    peer = None
    try:
        peer = await client.get_peer_id(entity)
    except Exception as e:
        LOGGER.debug(e)
    return peer


async def values_to_str(values_dict: dict) -> str:
    text = ""
    id_str = "[{0}](tg://user?id={0})"
    for key, values in values_dict.items():
        title = full_key_names.get(key, key)
        if len(text) == 0:
            text += f"**{title}:**\n  "
        else:
            text += f"\n\n**{title}**\n"
        if key == "tgid":
            text += ", ".join(id_str.format(x) for x in values)
        else:
            text += ", ".join(f'`{x}`' for x in values)
    return text
