# TG-UserBot - A modular Telegram UserBot for Python3.6+. 
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


from telethon import events
from userbot import client


def add_event(callback, event):
    client.add_event_handler(callback, event)


def remove_event(*args, **kwargs):
    disabled_handler = client.remove_event_handler(*args, **kwargs)
    return disabled_handler


def message(disable_edited=False, require_admin=False, **kwargs):
    pattern = kwargs.get('pattern', None)

    if pattern:
        kwargs['pattern'] = '(?i)' + pattern

    def wrapper(function):
        if not disable_edited:
            add_event(function, events.MessageEdited(**kwargs))
        add_event(function, events.NewMessage(**kwargs))
        return function
    
    return wrapper