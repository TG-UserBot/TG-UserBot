from os.path import basename, dirname, isfile, join
import glob

from userbot import DONT_LOAD
from userbot.modules.custom_modules import directory


modules = {}
custom_modules = {}
failed = []
didnt_load = []

modules_dir = glob.glob(join(dirname(__file__), "*.py"))
custom_modules_dir = glob.glob(join(dirname(directory), "*.py"))

def all_mods():
    for f in modules_dir:
        if isfile(f) and not f.endswith('__init__.py') and not f.startswith('_'):
            name = basename(f)[:-3]
            modules.update({name: 'userbot.modules.' + name})
    for f in custom_modules_dir:
        if isfile(f) and not f.endswith('__init__.py') and not f.startswith('_'):
            name = 'custom_modules.' + basename(f)[:-3]
            custom_modules.update({name: 'userbot.modules.' + name})
    
    for module, name in list(custom_modules.items()):
        if module in modules:
            del custom_modules[module]
            failed.append(name.strip('userbot.modules.'))
    
    to_import = {**modules, **custom_modules}
    for module in list(to_import.keys()):
        if module in DONT_LOAD:
            del to_import[module]
            didnt_load.append(module)
    
    return to_import, sorted(didnt_load), sorted(failed)

ALL_MODULES = all_mods()
__all__ = sorted(list(ALL_MODULES[0].keys()))