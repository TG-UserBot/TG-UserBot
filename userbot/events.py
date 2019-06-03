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