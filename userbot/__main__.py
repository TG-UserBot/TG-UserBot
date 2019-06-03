from sys import exit
from inspect import getmembers, isfunction
from importlib import import_module, invalidate_caches, reload

from userbot import client, __copyright__, LOG, __version__
from userbot.events import add_event, message, remove_event
from userbot.modules import ALL_MODULES


IMPORTED = []
IMPORTED_MODULES = {}

TO_IMPORT = ALL_MODULES[0]
DIDNT_LOAD = ALL_MODULES[1]
FAILED = ALL_MODULES[2]

for module, name in list(TO_IMPORT.items()):
    if module not in IMPORTED:
        imported_module = import_module(name)
        IMPORTED_MODULES.update({name: imported_module})
        IMPORTED.append(module)
    else:
        LOG.error("Cannot import multiple modules with the same name, quitting.")
        exit(1)

LOG.info(__copyright__)

if FAILED:
    LOG.error(f"Module(s) which failed to import: {FAILED}")
if DIDNT_LOAD:
    LOG.warning(f"Module(s) which wasn't/weren't imported: {DIDNT_LOAD}")

client.start()
LOG.info(f"Modules which were imported: {sorted(IMPORTED)}")
LOG.info(f"UserBot v{__version__} is running, test it with .ping in any chat.")

#############################################################################

KEEP_ALIVE = ['reloader', 'modules', 'handlers', 'enable', 'disable', 'disabled']
DISABLED_HANDLERS = {}

@message(disable_edited=True, outgoing=True, pattern=r'^.reload (.*)$')
async def reloader(event):
    await event.edit("**Reloading...**")
    to_reload = event.pattern_match.group(1)
    invalidate_caches()
    allow = None

    if to_reload != 'all':
        allow = to_reload if to_reload in IMPORTED_MODULES else None
    
    if allow:
        module = IMPORTED_MODULES[allow]
        functions = getmembers(module, predicate=isfunction)
        for function in functions:
            remove_event(function[1])
            if function[1] in DISABLED_HANDLERS:
                del DISABLED_HANDLERS[function[1]]
        reload(module)
        text = f"**Successfully reloaded:** __{allow}.__"
    elif to_reload == 'all':
        for handler in client.list_event_handlers():
            name = handler[0].__name__
            if name not in KEEP_ALIVE:
                remove_event(handler[0])
                if handler[0] in DISABLED_HANDLERS:
                    del DISABLED_HANDLERS[handler[0]]
        for module in IMPORTED_MODULES.items():
            reload(module[1])
            text = "**Successfully reloaded all modules.**"
    else:
        text = "Couldn't find the module."
    await event.edit(text)


@message(outgoing=True, pattern='^.modules$')
async def modules(event):
    mods = "**Imported modules:**"
    for mod in IMPORTED_MODULES:
        mods += "\n`" + mod + "`"
    await event.edit(mods)


@message(outgoing=True, pattern='^.handlers$')
async def handlers(event):
    header = "**Active event handler(s) for commands:**\n"
    text = ""
    for handler in client.list_event_handlers():
        text += ("\n" + handler[0].__name__)
    text_split = sorted(text.split())
    text = header + "\n".join(sorted(set(text_split), key=text_split.index))
    await event.edit(text)


@message(disable_edited=True, outgoing=True, pattern=r'^.enable (\w+)$')
async def enable(event):
    to_enable = event.pattern_match.group(1).lower()

    for handler in DISABLED_HANDLERS:
        function = handler if handler.__name__ == to_enable else None

    if not function:
        await event.edit("**Can't enable something that's not disabled.**")
        return
    else:
        for event_type in DISABLED_HANDLERS[function]:
            add_event(function, event_type)
        del DISABLED_HANDLERS[function]
    await event.edit(f"**Successfully enabled {to_enable}.**")


@message(disable_edited=True, outgoing=True, pattern=r'^.disable (\w+)$')
async def disable(event):
    to_disable = event.pattern_match.group(1).lower()
    status = 0
    
    for function, event_type in client.list_event_handlers():
        func_name = function.__name__
        if func_name == to_disable and func_name not in KEEP_ALIVE:
            if function in DISABLED_HANDLERS:
                DISABLED_HANDLERS[function].append(event_type)
            else:
                DISABLED_HANDLERS.update({function: [event_type]})
            status = remove_event(function, event_type)

    if status:
        text = f"**Successfully disabled {to_disable}.**"
    else:
        text = "**Couldn't find the specified function, or it's already disabled.**"
    await event.edit(text)


@message(outgoing=True, pattern='^.disabled$')
async def disabled(event):
    if DISABLED_HANDLERS:
        text = "**Disabled functions:**"
        for handler in DISABLED_HANDLERS:
            text += ("\n" + handler.__name__)
    else:
        text = "**There aren't any disabled event handlers.**"
    await event.edit(text)


#############################################################################

client.run_until_disconnected()