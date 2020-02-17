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
from typing import Dict, List

from telethon.events import ChatAction
from telethon.tl import types, functions

from userbot import client, LOGGER
from userbot.utils.events import NewMessage
from userbot.utils.sessions import RedisSession
from userbot.plugins.plugins_data import Blacklist, GlobalBlacklist


plugin_category = "blacklist"
if isinstance(type(client.session), type(RedisSession)):
    redis = client.session.redis_connection
else:
    redis = None

bl_pattern = (
    r"(?P<global>g(?:lobal)?)?"
    r"b(?:lack)?l(?:ist)?"
    r"(?: |$)"
    r"(?:(?P<option>\w+)[:=])?(?P<value>[\S]+|\".+\")?"
)
dbl_pattern = (
    r"r(?:e)?m(?:ove)?"
    r"(?P<global>g(?:lobal)?)?"
    r"b(?:lack)?l(?:ist)?"
    r"(?: |$)"
    r"(?:(?P<option>\w+)[:=])?(?P<value>[\S]+|\".+\")?"
)
wl_pattern = (
    r"w(?:hite)?l(?:ist)?"
    r"(?: |$)"
    r"(?P<value>@?\w{5,35}|\d{6,13})?"
)
dwl_pattern = (
    r"r(?:e)?m(?:ove)?"
    r"w(?:hite)?l(?:ist)?"
    r"(?: |$)"
    r"(?P<value>@?\w{5,35}|\d{6,13})?"
)
bls_pattern = (
    r"(?P<global>g(?:lobal)?)?"
    r"b(?:lack)?l(?:ist)?s"
    r"(?: |$)"
    r"(?:(?P<option>\w+))?"
)
wls_pattern = (
    r"w(?:hite)?l(?:ist)?s"
    r"(?: |$)"
    r"(?:(?P<option>\w+))?"
)
id_pattern = re.compile(
    r'(?:https?:\/\/)?(?:www\.)?(?:t\.me\/)?@?(?P<e>\w{5,35}|\d{6,13})\/?'
)
acceptable_options = {
    'id': 'tgid',
    'bio': 'bio',
    'string': 'txt',
    'str': 'txt',
    'domian': 'url',
    'url': 'url'
}
localBlacklists: Dict[int, Blacklist] = {}
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
    if redis.exists('whitelist:users'):
        whitelistedUsers = dill.loads(redis.get('whitelist:users'))
    if redis.exists('whitelist:chats'):
        whitelistedUsers = dill.loads(redis.get('whitelist:chats'))


async def append(key: str or bytes, option: str, value: str or int) -> int:
    """Create/Append values to keys in Redis DB"""
    if redis.exists(key):
        data = dill.loads(redis.get(key))
        if option in data and value in data[option]:
            return 1  # The value is already stored in the DB
        data.setdefault(option, []).append(value)
        data = dill.dumps(data)
    else:
        data = dill.dumps({option: [value]})
    redis.set(key, data)

    blkey = key[11:] if key.isalpha() else int(key[11:])
    if blkey == 'global':
        gval = getattr(GlobalBlacklist, option, []).append(value)
        setattr(GlobalBlacklist, option, gval)
    else:
        if blkey in localBlacklists:
            lval = getattr(localBlacklists[blkey], option)
            if lval:
                lval.append(value)
            setattr(localBlacklists[blkey], option, lval)
        else:
            localBlacklists[blkey] = Blacklist({option: [value]})

    return 0  # The value was stored in the DB


async def unappend(key: str or bytes, option: str, value: str or int) -> int:
    """Remove/Unappend values to keys from Redis DB"""
    empty = False
    if redis.exists(key):
        data = dill.loads(redis.get(key))
        if option in data and value in data[option]:
            data[option].remove(value)
            for x, _ in data.copy().items():
                if len(data[x]) == 0:
                    del data[x]
            if len(data) == 0:
                empty = True
            else:
                data = dill.dumps(data)
        else:
            return 1  # The value doesn't exist in the list
    else:
        return 2  # The key doesn't exist
    if empty:
        redis.delete(key)
    else:
        redis.set(key, data)

    blkey = key[11:] if key.isalpha() else int(key[11:])
    if blkey == 'global':
        gval = getattr(GlobalBlacklist, option, [])
        if value in gval:
            gval.remove(value)
        setattr(GlobalBlacklist, option, gval)
    else:
        if blkey in localBlacklists:
            lval = getattr(localBlacklists[blkey], option, [])
            if value in lval:
                lval.remove(value)
            setattr(localBlacklists[blkey], option, lval)

    return 0  # The value was removed from the DB


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
    option = event.matches[0].group('option') or 'str'
    value = event.matches[0].group('value')
    key = "global" if glb else str(event.chat_id)

    if not value:
        await event.answer('__.(g)bl <option>:<value>__')
        return

    if not glb:
        chat = await event.get_chat()
        if not chat.creator:
            if not getattr(chat.admin_rights, 'ban_users', False):
                await event.edit(
                    "`You need to have ban rights to set a blacklist in here.`"
                )
                return

    if option and option not in acceptable_options:
        await event.answer(
            "`Invalid argument. Available options:`\n"
            "__id, bio, string/str, domain/url__"
        )
        return

    option = acceptable_options.get(option, 'txt')
    if value.startswith('"') and value.endswith('"'):
        value = value.strip('"')
    if option == 'tgid':
        entity = id_pattern.search(value).group('e')
        try:
            value = await client.get_peer_id(entity)
        except Exception:
            await event.answer("`Invalid ID.`")
            return

    response = await append("blacklists:" + key, option, value)
    if response == 0:
        await event.answer(
            f'__Added {option} blacklist:__ **{value}** __for {key}.__',
            log=('blacklist', f'Added {option} blacklist: {value} for {key}.')
        )
    else:
        await event.answer(
            f'__Skipped {option} blacklist, it already exists for {key}.__',
            reply=True
        )


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
    option = event.matches[0].group('option') or 'str'
    value = event.matches[0].group('value')
    key = "global" if glb else str(event.chat_id)

    if not value:
        await event.answer('__.rm(g)bl <option>:<value>__')
        return

    if option and option not in acceptable_options:
        await event.answer(
            "`Invalid argument. Available options:`\n"
            "__id, bio, string/str, domain/url__"
        )
        return

    option = acceptable_options.get(option, 'txt')
    if value.startswith('"') and value.endswith('"'):
        value = value.strip('"')
    response = await unappend("blacklists:" + key, option, value)
    if response == 0:
        await event.answer(
            f'__Removed {option} blacklist:__ **{value}** __for {key}.__',
            log=(
                'blacklist', f'Removed {option} blacklist: {value} for {key}.'
            )
        )
    elif response == 1:
        await event.answer(
            f"__Skipped {option} blacklist, it doesn't exists for {key}.__",
            reply=True
        )
    else:
        await event.answer(
            f"__There are no blackists saved for {key}.__",
            reply=True
        )


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

    value = event.matches[0].group('value')
    user = False
    chat = False

    if not value:
        if event.reply_to_msg_id:
            wl = (await event.get_reply_message()).from_id
            wl = await client.get_peer_id(wl)
            user = True
        else:
            wl = await client.get_peer_id(await event.get_input_chat())
            chat = True
    else:
        value = int(value) if value.isdigit() else value
        try:
            entity = await event.get_input_entity(value)
            if isinstance(entity, types.InputPeerUser):
                user = True
            else:
                chat = True
            wl = await client.get_peer_id(entity)
        except Exception:
            await event.answer(f"__Couldn't get the entity for {value}.__")
            return

    if wl in whitelistedUsers or wl in whitelistedChats:
        await event.answer(f'__{wl} is already whitelisted.__')
        return

    if user:
        whitelistedUsers.append(wl)
        redis.set('whitelist:users', dill.dumps(whitelistedUsers))
        await event.answer(
            f"**Successfully whitelisted** [{wl}](tg://user?id={wl})"
        )
    elif chat:
        whitelistedChats.append(wl)
        redis.set('whitelist:chats', dill.dumps(whitelistedUsers))
        await event.answer(f"**Successfully whitelisted chat** `{wl}`")
    else:
        await event.answer("__IDK what happened?__")


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

    value = event.matches[0].group('value')
    if event.reply_to_msg_id and not value:
        value = (await event.get_reply_message()).from_id
    if not value:
        value = event.chat_id

    if not value:
        await event.answer('__.rmwl (<value>)__')
        return

    if value in whitelistedUsers:
        whitelistedUsers.remove(value)
        if whitelistedUsers:
            redis.set('whitelist:users', dill.dumps(whitelistedUsers))
        else:
            redis.delete('whitelist:users')
        await event.answer(f"__Removed user {value} from whitelist.__")
    elif value in whitelistedChats:
        whitelistedChats.remove(value)
        if whitelistedChats:
            redis.set('whitelist:chats', dill.dumps(whitelistedUsers))
        else:
            redis.delete('whitelist:chats')
        await event.answer(f"__Removed chat {value} from whitelist.__")
    else:
        await event.answer(f"__{value} hasn't been whitelisted.__")
        return


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
    option = event.matches[0].group('option') or None

    if option and option not in acceptable_options:
        await event.answer(
            "`Invalid argument. Available options:`\n"
            "__id, bio, string/str, domain/url__"
        )
        return

    if glb:
        if (
            len(GlobalBlacklist.txt) + len(GlobalBlacklist.url) +
            len(GlobalBlacklist.bio) + len(GlobalBlacklist.tgid) == 0
        ):
            await event.answer("__There are no global blacklists.__")
            return
        if option:
            attr = getattr(GlobalBlacklist, option, None)
            if attr:
                values = ', '.join(attr)
                text = f"**GLobal {option} blacklists:**\n```{values}```"
            else:
                text = f"__There are no global {option} blacklists.__"
        else:
            text = "**Global blacklists:**\n"
            text += await blattributes(GlobalBlacklist)
    else:
        if event.chat_id not in localBlacklists:
            await event.answer('__There are no blacklists set here.__')
            return
        if option:
            attr = getattr(localBlacklists[event.chat_id], option, None)
            if attr:
                values = ', '.join(attr)
                text = f"**{option.title()} blacklists:**\n```{values}```"
            else:
                text = f"__There are no {option} blacklists.__"
        else:
            text = "**Blacklists:**\n"
            text += await blattributes(localBlacklists[event.chat_id])

    await event.answer(text)


@client.onMessage(
    command=("whitelists", plugin_category),
    outgoing=True, regex=wls_pattern
)
async def listwls(event: NewMessage.Event) -> None:
    """Get a list of all the (global) whitelists"""
    if not redis:
        await event.answer(
            "`You need to use a Redis session to use blacklists.`"
        )
        return

    option = event.matches[0].group('option') or None

    if option and option not in ['users', 'chats', 'user', 'chat']:
        await event.answer(
            "`Invalid argument. Available options:`\n"
            "__user(s) or chat(s)__"
        )
        return

    if option:
        if option in ['user', 'users']:
            if whitelistedUsers:
                text = "**Whitelisted users:**\n"
                text += ', '.join([str(x) for x in whitelistedUsers])
            else:
                text = "__There are no whitelisted users.__"
        else:
            if whitelistedChats:
                text = "**Whitelisted chats:**\n"
                text += ', '.join([str(x) for x in whitelistedChats])
            else:
                text = "__There are no whitelisted chats.__"
    else:
        if not whitelistedChats and not whitelistedUsers:
            text = "__There are no whitelisted users or chats.__"
        else:
            text = ""

        if whitelistedUsers:
            text += "**Whitelisted users:**\n"
            text += ', '.join([str(x) for x in whitelistedUsers])
        if whitelistedChats:
            text += "\n**Whitelisted chats:**\n"
            text += ', '.join([str(x) for x in whitelistedChats])

    await event.answer(text)


@client.onMessage(incoming=True)
async def inc_listner(event: NewMessage.Event) -> None:
    """Filter incoming messages for blacklisting."""
    if not redis:
        return
    if event.chat_id in whitelistedChats or event.from_id in whitelistedUsers:
        return

    text = False
    flag = False
    tgid_check = False
    localbl = localBlacklists.get(event.chat_id, False)

    if GlobalBlacklist.txt:
        for value in GlobalBlacklist.txt:
            string = await escape_string(value)
            if re.search(string, event.text, flags=re.I):
                text = (
                    "**Banned due to globally blacklisted string match: "
                    f"{value}**"
                )
    elif localbl and getattr(localbl, 'string', False):
        for value in localBlacklists[event.chat_id].txt:
            string = await escape_string(value)
            if re.search(string, event.text, flags=re.I):
                text = f"**Banned due to blacklisted string match: {value}**"
    if text:
        flag = await ban_user(event, text)
        if flag:
            return

    if GlobalBlacklist.url:
        for value in GlobalBlacklist.url:
            string = re.sub(r'(?<!\\)\*', r'\\w+', value, count=0)
            if re.search(string, event.text, flags=re.I):
                text = (
                    "**Banned due to globally blacklisted url match: "
                    f"{value}**"
                )
    elif localbl and getattr(localbl, 'url', False):
        for value in localBlacklists[event.chat_id].url:
            string = re.sub(r'(?<!\\)\*', r'\\w+', value, count=0)
            if re.search(string, event.text, flags=re.I):
                text = f"**Banned due to blacklisted url match: {value}**"
    if text:
        flag = await ban_user(event, text)
        if flag:
            return

    if GlobalBlacklist.tgid or (localbl and getattr(localbl, 'tgid', False)):
        tgid_check = True

    if tgid_check and event.entities:
        for entity in event.entities:
            if (
                isinstance(
                    entity,
                    (types.MessageEntityMention, types.MessageEntityUrl)
                )
            ):
                entity = id_pattern.search(
                    event.text[entity.offset:entity.offset+entity.length]
                ).group('e')
                value = await client.get_peer_id(entity) if entity else 0
            elif isinstance(entity, types.MessageEntityMentionName):
                value = await client.get_peer_id(entity.user_id)

            if GlobalBlacklist.tgid and value in GlobalBlacklist.tgid:
                text = (
                    "**Banned due to globally blacklisted url match: "
                    f"{value}**"
                )
            elif value in localBlacklists[event.chat_id].tgid:
                text = f"**Banned due to blacklisted id match: {value}**"
    if text:
        flag = await ban_user(event, text)
        if flag:
            return


@client.on(ChatAction)
async def bio_filter(event: ChatAction.Event) -> None:
    """Filter incoming messages for blacklisting."""
    if not redis:
        return
    text = None

    if event.user_added or event.user_joined:
        try:
            sender = await event.get_input_user()
            chat = await event.get_chat()
            sender_id = await client.get_peer_id(sender)
            chat_id = await client.get_peer_id(chat)
            localbl = localBlacklists.get(chat_id, False)
        except (ValueError, TypeError):
            return
        if chat_id in whitelistedChats or sender_id in whitelistedUsers:
            return

        user = await client(functions.users.GetFullUserRequest(id=sender))
        if GlobalBlacklist.bio:
            for value in GlobalBlacklist.bio:
                bio = await escape_string(value)
                if re.search(bio, user.about, flags=re.I):
                    text = (
                        "**Banned due to globally blacklisted bio match: "
                        f"{value}**"
                    )
        elif localbl and getattr(localbl, 'bio', False):
            for value in localBlacklists[chat_id].bio:
                bio = await escape_string(value)
                if re.search(bio, user.about, flags=re.I):
                    text = f"**Banned due to blacklisted bio match: {value}**"

        if text:
            if not (chat.creator or chat.admin_rights.ban_user):
                return
            try:
                await client.edit_permissions(
                    entity=chat,
                    user=sender_id,
                    view_messages=False
                )
                await event.reply(text)
                if client.logger:
                    logger_group = client.config['userbot'].getint(
                        'logger_group_id', 'me'
                    )
                    log_text = (
                        "**USERBOT LOG** #blacklist\n"
                        f'Banned {sender_id} from {chat_id}.\n{text}.'
                    )
                    await client.send_message(logger_group, log_text)
            except Exception as e:
                await event.reply(f"**Couldn't ban user due to {e}**")
                LOGGER.exception(e)


async def escape_string(string: str) -> str:
    """Literal match everything but * and ?"""
    string = re.sub(r'(?<!\\)\*', '.+', string, count=0)
    string = re.sub(r'(?<!\\)\?', '.', string, count=0)
    return string


async def ban_user(event: NewMessage.Event, text: str) -> bool:
    chat = await event.get_chat()
    if not (chat.creator or chat.admin_rights.ban_user):
        return False
    try:
        await client.edit_permissions(
            entity=event.chat_id,
            user=event.from_id,
            view_messages=False
        )
        await event.answer(
            text,
            log=(
                'blacklist',
                f'Banned {event.from_id} from {event.chat_id}.\n{text}.'
            )
        )
        return True
    except Exception as e:
        await event.answer(f"**Couldn't ban user due to {e}**", reply=True)
        LOGGER.exception(e)
        return False


async def blattributes(blacklist) -> str:
    """Get all the available attributes from a BL class"""
    text = ""
    strings = getattr(blacklist, 'txt', None)
    bio = getattr(blacklist, 'bio', None)
    tgid = getattr(blacklist, 'tgid', None)
    url = getattr(blacklist, 'url', None)
    if strings:
        text += f"\n**[String]:** ```{', '.join(strings)}```\n"
    if bio:
        text += f"\n**[Bio]:** ```{', '.join(bio)}```\n"
    if tgid:
        text += f"\n**[ID]:** ```{', '.join([str(x) for x in tgid])}```\n"
    if url:
        text += f"\n**[URL]:** ```{', '.join(url)}```\n"
    return text
