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

from dataclasses import dataclass
from importlib import invalidate_caches, util
from inspect import iscoroutinefunction
from logging import getLogger
from os.path import relpath
from pathlib import Path
from telethon.events import _get_handlers
from types import ModuleType
from typing import List


LOGGER = getLogger("Plugin Manager")


@dataclass
class Callback:
    name: str
    callback: callable


@dataclass
class Plugin:
    name: str
    callbacks: List[Callback]
    path: str
    module: ModuleType


class PluginManager:
    active_plugins: List[Plugin] = []
    inactive_plugins: List[Plugin] = []

    def __init__(self, client):
        self.client = client
        config = client.config["plugins"]
        self.plugin_path: str = relpath(
            config.get("root", "./userbot/plugins")
        )
        self.include: list = self._split_plugins(config.get("include", []))
        self.exclude: list = self._split_plugins(config.get("exclude", []))

    def import_all(self):
        invalidate_caches()
        for plugin_name, path in self._list_plugins():
            if self.include and not self.exclude:
                if plugin_name in self.include:
                    self._import_module(plugin_name, path)
                else:
                    self.inactive_plugins.append(
                        Plugin(plugin_name, [], path, None)
                    )
            elif not self.include and self.exclude:
                if plugin_name in self.exclude:
                    self.inactive_plugins.append(
                        Plugin(plugin_name, [], path, None)
                    )
                    LOGGER.debug("Skipped importing %s", plugin_name)
                else:
                    self._import_module(plugin_name, path)
            else:
                self._import_module(plugin_name, path)

    def add_handlers(self):
        for plugin in self.active_plugins:
            for callback in plugin.callbacks:
                self.client.add_event_handler(callback.callback)
                LOGGER.debug(
                    "Added event handler for %s.", callback.__class__.__name__
                )

    def remove_handlers(self):
        for plugin in self.active_plugins:
            for callback in plugin.callbacks:
                self.client.remove_event_handler(callback.callback)
                LOGGER.debug(
                    "Removed event handlers for %s.",
                    callback.__class__.__name__
                )

    def _list_plugins(self):
        plugins: List[str, str] = []
        if self.client.config["plugins"].getboolean("enabled", False):
            for f in Path(self.plugin_path).glob("**/*.py"):
                if f.name != "__init__.py" and not f.name.startswith('_'):
                    name = f.name[:-3]
                    path = relpath(f)[:-3].replace("\\", ".")
                    plugins.append((name, path))
        return plugins

    def _import_module(self, name: str, path: str):
        for plugin in self.active_plugins:
            if plugin.name == name:
                LOGGER.error(
                    "Rename the plugin %s in %s or %s and try again.",
                    name, path, plugin.path
                )
                exit(1)
        try:
            path = path.replace('/', '.')
            spec = util.find_spec(path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # To make plugins impoartable use "sys.modules[path] = module".
            callbacks: List[Callback] = []
            for n, cb in vars(module).items():
                if iscoroutinefunction(cb) and not n.startswith('_'):
                    if _get_handlers(cb):
                        callbacks.append(Callback(n, cb))
            self.active_plugins.append(Plugin(name, callbacks, path, module))
            LOGGER.info("Successfully Imported %s", name)
        except Exception as E:
            LOGGER.error(
                "Failed to import %s due to the error(s) below.", path
            )
            LOGGER.exception(E)

    def _split_plugins(self, to_split: str or list):
        if isinstance(to_split, str):
            if ',' in to_split:
                sep = ','
            else:
                sep = "\n"
            return to_split.split(sep)
        else:
            return to_split
