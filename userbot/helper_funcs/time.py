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


from re import compile as reCompile


regexp = reCompile(r"(\d+)(w|d|h|m|s)?")


async def amount_to_secs(amount):
    num, unit = amount

    num = int(num)
    if not unit:
        unit = 's'

    if unit == 's':
        return num
    elif unit == 'm':
        return num*60
    elif unit == 'h':
        return num*60*60
    elif unit == 'd':
        return num*60*60*24
    elif unit == 'w':
        return num*60*60*24*7
    else:
        return 0


async def string_to_secs(string):
    values = regexp.findall(string)

    totalValues = len(values)

    if totalValues == 1:
        return await amount_to_secs(values[0])
    else:
        total = 0
        for amount in values:
            total += await amount_to_secs(amount)
        return total