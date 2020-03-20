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


# This is based on the parser of https://github.com/mojurasu/kantek/


import re
from typing import Dict, List, Tuple, Union


KWARGS = re.compile(
    r'(?<!\S)'  # Make sure the key starts after a whitespace
    r'(?:(?P<q>\'|\")?)(?P<key>(?(q).+?|(?!\d)\w+?))(?(q)(?P=q))'
    r'(?::(?!//)|=)\s?'
    r'(?P<val>\[.+?\]|(?P<q1>\'|\").+?(?P=q1)|\S+)'
)
ARGS = re.compile(r'(?:(?P<q>\'|\"))(.+?)(?:(?P=q))')
BOOL_MAP = {
    'false': False,
    'true': True,
}

Value = Union[int, str, float, list]
KeywordArgument = Union[Value, range, List[Value]]


async def _parse_arg(val: str) -> Union[int, str, float]:
    if val.isdecimal():
        return int(val)

    try:
        return float(val)
    except ValueError:
        pass

    if isinstance(val, str):
        if re.search(r'^\[.*\]$', val):
            val = re.sub(r'[\[\]]', '', val).split(',')
            val = [await _parse_arg(v.strip()) for v in val]
        else:
            val = BOOL_MAP.get(val.lower(), val)
    if isinstance(val, str):
        val = re.sub(r'(?<!\\), ?$', '', val)
    return val


async def parse_arguments(
    arguments: str
) -> Tuple[List[Value], Dict[str, KeywordArgument]]:
    keyword_args = {}
    args = []

    for match in KWARGS.finditer(arguments):
        key = match.group('key')
        val = await _parse_arg(re.sub(r'[\'\"]', '', match.group('val')))
        keyword_args.update({key: val})
    arguments = KWARGS.sub('', arguments)

    for val in ARGS.finditer(arguments):
        args.append(val.group(2).strip())
    arguments = ARGS.sub('', arguments)

    for val in re.findall(r'([^\r\n\t\f\v ,]+|\[.*\])', arguments):
        parsed = await _parse_arg(val)
        if parsed:
            args.append(val)
    return args, keyword_args
