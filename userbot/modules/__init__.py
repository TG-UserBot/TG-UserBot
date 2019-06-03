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