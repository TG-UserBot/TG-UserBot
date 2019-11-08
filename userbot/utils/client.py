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


import configparser
import dataclasses
import importlib
import logging
import sys
from typing import Dict, List

from telethon import TelegramClient, events

from .pluginManager import PluginManager
from .events import MessageEdited, NewMessage


LOGGER = logging.getLogger(__name__)
no_info = "There is no help available for this command!"


@dataclasses.dataclass
class Command:
    func: callable
    handlers: list
    info: str
    builtin: bool


class UserBotClient(TelegramClient):
    """UserBot client with additional attributes inheriting TelegramClient"""
    commandcategories: Dict[str, List[str]] = {}
    commands: Dict[str, Command] = {}
    config: configparser.ConfigParser = None
    disabled_commands: Dict[str, Command] = {}
    failed_imports: list = []
    logger: bool = False
    pluginManager: PluginManager = None
    plugins: list = []
    prefix: str = None
    restarting: bool = False
    register_commands: bool = False
    running_processes: dict = {}
    version: int = 0

    def onMessage(
        self,
        builtin: bool = False,
        command: str or tuple = None,
        edited: bool = True,
        info: str = None,
        **kwargs
    ) -> callable:
        """Method to register a function without the client"""

        kwargs.setdefault('forwards', False)

        def wrapper(func: callable) -> callable:
            events.register(NewMessage(**kwargs))(func)

            if edited:
                events.register(MessageEdited(**kwargs))(func)

            if self.register_commands and command:
                handlers = events._get_handlers(func)
                category = "misc"
                com = command
                if isinstance(command, tuple):
                    if len(command) == 2:
                        com, category = command
                    else:
                        raise ValueError

                UBcommand = Command(
                    func,
                    handlers,
                    info or func.__doc__ or no_info,
                    builtin
                )
                category = category.lower()
                self.commands.update({com: UBcommand})

                update_dict(self.commandcategories, category, com)
                if builtin:
                    update_dict(self.commandcategories, 'builtin', com)
            return func

        return wrapper

    async def _restarter(self, event: NewMessage.Event) -> None:
        """Remove all event handlers and stop then start the client again"""
        if self.restarting:
            await event.answer("`Previous restart is still in proccess!`")
            return

        self.failed_imports.clear()
        self.restarting = True

        self._kill_running_processes()

        await event.answer(
            "`Removing all the event handlers and disonnecting "
            "the client. BRB.`"
        )
        self.pluginManager.remove_handlers()
        self.pluginManager.inactive_plugins = []
        self.pluginManager.active_plugins = []
        self.commands.clear()
        self.disabled_commands.clear()
        await self.disconnect()

        for module in sys.modules.copy():
            # Required to update helper and util file.
            if module.startswith(('userbot.helper_funcs.', 'userbot.utils.')):
                importlib.reload(sys.modules[module])

        await self.connect()
        await event.answer(
            "`Succesfully removed all the handlers and started "
            "the client again! Adding the new handlers now. BRB..`"
        )
        self.pluginManager.import_all()
        self.pluginManager.add_handlers()

        text = "`Successfully restarted and imported all the plugins!`"
        if self.failed_imports:
            text = (
                "`Couldn't import all the plugins. Check the console logs or"
                " do a manual restart.`"
            )
            text += "\n`Failed imports:`\n"
            text += '\n'.join(self.failed_imports)
            self.failed_imports.clear()
        await event.answer(
            text,
            log=("restart client", "Successfully restarted the client")
        )

        self.restarting = False
        LOGGER.info(
            "Client restarted! Current prefix: {}".format(self.prefix)
        )
        print()

    def _updateconfig(self) -> bool:
        """Update the config. Sync method to avoid issues."""
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)
        return True

    def _kill_running_processes(self) -> None:
        """Kill all the running asyncio subprocessess"""
        for _, process in self.running_processes.items():
            process.kill()
            LOGGER.debug("Killed %d which was still running.", process.pid)
        self.running_processes.clear()


def update_dict(category: dict, name: str, command: str or list) -> None:
    commands = command.split('/') if '/' in command else [command]
    for c in commands:
        category.setdefault(name, []).append(c)
