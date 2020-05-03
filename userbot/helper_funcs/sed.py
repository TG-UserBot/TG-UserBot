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
from enum import Enum
from typing import Tuple, Union


caseConversions = (r'\U', r'\L', r'\E', r'\u', r'\l', r'\I', r'\F')
endCaseConversions = {
    r'\U': r'\\EU',
    r'\L': r'\\EL',
    r'\I': r'\\EI',
    r'\F': r'\\EF'
}


class UnknownFlagError(Exception):
    """Used to raise an Exception for an unknown flag."""
    def __init__(self, flag):
        super().__init__(flag)
        self.flag = flag


async def match_splitter(match: re.Match) -> Tuple[str, str, str, str]:
    """Splits an :obj:`re.Match` to get the required attributes for substitution.
    Unescapes the slashes as well because this is Python.

    Args:
        match (:obj:`Match<re.match>`):
            Match object to split.

    Returns:
        (``str``, ``str``, ``str``, ``str``):
            A tuple of strings containing
            line, regexp, replacement and flags respectively.
    """
    li = match.group(1)
    fr = match.group(3)
    to = match.group(4) if match.group(4) else ''
    to = re.sub(r'\\/', '/', to)
    for c in caseConversions:
        case = re.escape(c)
        exp = re.compile(r'(?<!\\)' + case + r'(\d+)?')
        while True:
            tmp = exp.search(to)
            if not tmp:
                break
            start, end = tmp.span()
            group = tmp.group(1) or ''
            if group:
                group = r"\g<0>" if group == '0' else '\\' + group
                group += endCaseConversions.get(c, '')
            to = to.replace(to[start:end], case + group)
    to = re.sub(r'(?<!\\)\\0', r'\g<0>', to)
    fl = match.group(5) if match.group(5) else ''

    return li, fr, to, fl


async def resolve_flags(fl: str) -> Tuple[int, Union[int, Enum]]:
    """Split all flags from the string for substituion.

    Args:
        fl (``str``):
            String containing all the flags.

    Raises:
        UnknownFlagError:
            If there's an unknown flag, then this is raised
            to stop any farther execution.

    Returns:
        (``int``, (``int`` | :obj:`enum.Enum<enum>`)):
            Count and all the other re flags as an Enum type, if any.
    """
    count = 1
    flags = 0

    for f in fl.lower():
        if f == 'a':
            flags |= re.ASCII
        elif f == 'i':
            flags |= re.IGNORECASE
        elif f == 'l':
            flags |= re.LOCALE
        elif f == 'm':
            flags |= re.MULTILINE
        elif f == 's':
            flags |= re.DOTALL
        elif f == 'u':
            flags |= re.UNICODE
        elif f == 'x':
            flags |= re.VERBOSE
        elif f == 'g':
            count = 0
        else:
            raise UnknownFlagError(f)

    return count, flags


async def convertCharacterCase(string: str, case: str) -> str:
    """Convert the case of a character if found. Used for \\u and \\l.

    Args:
        string (``str``):
            The string containing the case.
        case (``str``):
            The raw string of the case.

    Returns:
        ``str`` | ``None``:
            The replaced string on success, None otherwise.
    """
    case = re.escape(case)
    match = re.search(case, string)
    if match:
        start, end = match.span()
        repl = string[end]
        tmp = repl.upper() if case == r"\\u" else repl.lower()
        string = string[:end-2] + tmp + string[end+1:]
    return string


async def convertStringCase(string: str, case: str) -> str:
    """Convert the matched string in the necessary case. Used for \\U and \\L.

    Args:
        string (``str``):
            The string containing the case.
        case (``str``):
            The case to search for.

    Returns:
        ``str`` | ``None``:
            The replaced string on success, None otherwise.
    """
    opp = r"\\L" if case == r"\\U" else r"\\U"
    trmintr = endCaseConversions.get(case)
    exp = "({}).+?({}|{}|{}|$)".format(re.escape(case), trmintr, opp, r'\\E')
    match = re.search(exp, string, flags=re.DOTALL)
    if match:
        start, end = match.span()
        toStrip = match.group(1)
        terminator = match.group(2)
        if terminator:
            tend = -2 if terminator == r"\E" else -3
            tmp = match.group(0)
            if toStrip == r"\U":
                string = string[:start] + tmp.upper()[2:tend] + string[end:]
            else:
                string = string[:start] + tmp.lower()[2:tend] + string[end:]
        else:
            tmp = string[start:]
            if toStrip == r"\U":
                string = string[:start] + tmp.upper()[2:]
            else:
                string = string[:start] + tmp.lower()[2:]
    return string


async def convertWordCase(string: str, case: str) -> str:
    """Convert the matched words in the necessary case. Used for \\F and \\I.

    Args:
        string (``str``):
            The string containing the case.
        case (``str``):
            The case to search for.

    Returns:
        ``str`` | ``None``:
            The replaced string on success, None otherwise.
    """
    trmintr = endCaseConversions.get(case)
    exp = "({}).+?({}|{}|$)".format(re.escape(case), trmintr, r'\\E')
    match = re.search(exp, string, flags=re.DOTALL)
    if match:
        start, end = match.span()
        toStrip = match.group(1)
        terminator = match.group(2)
        if terminator:
            tend = -2 if terminator == r"\E" else -3
            tmp = match.group(0)
            tmp1 = tmp[2:tend]
            if toStrip == r"\F":
                repl = tmp1[0].upper() + tmp1[1:].lower()
                string = string[:start] + repl + string[end:]
            else:
                string = string[:start] + tmp1.title() + string[end:]
        else:
            tmp = string[start:]
            tmp1 = tmp[2:]
            if toStrip == r"\F":
                string = string[:start] + tmp1[0].upper() + tmp1[1:].lower()
            else:
                string = string[:start] + tmp1.title()
    return string


async def substitute(
    fr: str,
    to: str,
    original: str,
    line: (str, int, None) = None,
    count: int = 1,
    flags: Union[Enum, int] = 0
) -> Union[str, None]:
    """Substitute a (specific) string.
    Match the regular-expression against the content of the pattern space.
    If found, replace matched string with replacement.

    Args:
        fr (``str``):
            The regexp string.
        to (``str``):
            The replacement string.
        original (``str``):
            Original string to use for substituion.
        line (``str`` | ``int`` | ``None``, optional):
            Line to use for substitution. Defaults to None.
        count (``int``, optional):
            The amount of repetitions to do. Defaults to 1.
        flags (``int`` | :obj:`enum.Enum<enum>`, optional):
            Flags to use. Defaults to 0.

    Returns:
        ``str`` | ``None``:
            The replaced string on success, None otherwise.
    """
    newStr = None
    if line:
        line = int(line)
        lines = original.splitlines()
        if len(lines) < line:
            return
        newLine, i = re.subn(
            fr, to, lines[line - 1], count=count, flags=flags
        )
        if i == 0:
            return
        lines[line - 1] = newLine
        newStr = '\n'.join(lines)
    else:
        newStr, i = re.subn(fr, to, original, count=count, flags=flags)
        if i == 0:
            return

    for i in (r'\U', r'\L'):
        while i in newStr:
            newStr = await convertStringCase(newStr, i)
    for i in (r'\u', r'\l'):
        while i in newStr:
            newStr = await convertCharacterCase(newStr, i)
    for i in (r'\I', r'\F'):
        while i in newStr:
            newStr = await convertWordCase(newStr, i)

    return newStr


async def sub_matches(matches: list, original: str) -> Union[str, None]:
    """Iterate over all the matches whilst substituing the string.

    Args:
        matches (``list``):
            A list of :obj:`Match<re.match>` objects.
        original (``str``):
            The original string to use for substituion.

    Returns:
        ``str`` | ``None``:
            The final substitued string on success, None otherwise.
    """
    string = original
    total_subs = 0

    for match in matches:
        line, fr, to, fl = await match_splitter(match)
        try:
            count, flags = await resolve_flags(fl)
        except UnknownFlagError as f:
            exc = f"`Unknown flag:` `{f}`"
            return exc

        newStr = await substitute(
            fr,
            to,
            string,
            line=line,
            count=count,
            flags=flags
        )
        if newStr:
            string = newStr
            total_subs += 1

    if total_subs > 0:
        return string

    return
