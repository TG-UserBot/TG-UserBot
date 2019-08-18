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


# This is based on https://github.com/SijmenSchoon/regexbot
# but slightly different.
# https://stackoverflow.com/a/46100580 is also very helpful with the
# explanation on how we could make it work and what we'd need to check.


from re import match, MULTILINE, IGNORECASE

from userbot.events import commands, Filters, on_message
from userbot.helper_funcs.sed import sub_matches


pattern = (
    r'(?:^|;.+?)'  # Ensure that the expression doesn't go blatant
    r'([1-9]+?)?'  # line: Don't match a 0, sed counts lines from 1
    r'(?:s)'  # The s command (as in substitute)
    r'(?:(?P<d>.))'  # Unknown delimiter with a named group d
    r'((?:(?!(?<![^\\]\\)(?P=d)).)+)'  # regexp
    r'(?P=d)'  # Unknown delimiter
    r'((?:(?!(?<![^\\]\\)(?P=d)|(?<![^\\]\\);).)*)'  # replacement
    r'(?:(?=(?P=d)|;).)?'  # Check if it's a delimiter or a semicolon
    r'((?<!;)\w+)?'  # flags: Don't capture if it starts with a semicolon
    r'(?=;|$)'  # Ensure it ends with a semicolon for the next match
)


@commands("sed")
@on_message(Filters.outgoing & Filters.regex(pattern, MULTILINE | IGNORECASE))
async def sed_substitute(client, event):
    """SED function used to substitution texts for s command"""
    if not match(r"(?i)^(?:s|[1-9]+s)", event.text):
        return

    matches = event.matches
    reply = event.reply_to_message

    try:
        if reply:
            original = reply.text or reply.caption
            if not original:
                return

            newStr = await sub_matches(matches, original)
            if newStr:
                await event.edit(newStr)
        else:
            total_messages = []  # Append messages to avoid timeouts
            count = 0  # Don't fetch more than ten texts/captions

            async for msg in client.iter_history(
                event.chat.id,
                offset_id=event.message_id
            ):
                if msg.text:
                    total_messages.append(msg.text)
                    count += 1
                elif msg.caption:
                    total_messages.append(msg.caption)
                    count += 1
                else:
                    continue
                if count >= 10:
                    break

            for message in total_messages:
                newStr = await sub_matches(matches, message)
                if newStr:
                    await event.edit(newStr)
                    break
    except Exception as e:
        await event.edit((
            f"{event.text}"
            '\n\n'
            'Like regexbox says, fuck me.\n'
            '`'
            f"{str(type(e))}"
            ':` `'
            f"{str(e)}"
            '`'
        ))
