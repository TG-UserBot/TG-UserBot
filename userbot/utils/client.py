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


from configparser import ConfigParser
from dataclasses import dataclass
from importlib import reload
from logging import getLogger
from sys import modules
from telethon import TelegramClient, events

import userbot.utils.pluginManager as PluginManager
import userbot.utils.events as custom_events


LOGGER = getLogger("UserBot Client")


@dataclass
class Command:
    func: callable
    handlers: list
    info: str
    builtin: bool


class UserBotClient(TelegramClient):
    """UserBot client with additional attributes inheriting TelegramClient"""
    commands: dict = {}
    config: ConfigParser = None
    disabled_commands: dict = {}
    failed_imports: list = []
    pluginManager: PluginManager.PluginManager = None
    plugins: list = []
    prefix: str = None
    restarting: bool = False
    register_commands: bool = False
    running_processes: dict = {}
    version: int = 0

    def onMessage(
        self,
        builtin: bool = False,
        command: str = None,
        edited: bool = True,
        info: str = None,
        **kwargs
    ) -> callable:
        """Method to register a function without the client"""
        NewMessage = custom_events.NewMessage
        MessageEdited = custom_events.MessageEdited

        kwargs.setdefault('forwards', False)

        def wrapper(func):
            events.register(NewMessage(**kwargs))(func)

            if edited:
                events.register(MessageEdited(**kwargs))(func)

            if self.register_commands and command:
                handlers = events._get_handlers(func)
                self.commands.update(
                    {command: Command(func, handlers, info, builtin)}
                )

            return func

        return wrapper

    async def _restarter(self, event):
        if self.restarting:
            await event.edit("`Previous restart is still in proccess!`")
            return

        self.failed_imports.clear()
        self.restarting = True

        self._kill_running_processes()

        await event.edit(
            "`Removing all the event handlers and disonnecting "
            "the client. BRB.`"
        )
        self.pluginManager.remove_handlers()
        self.pluginManager.inactive_plugins = []
        self.pluginManager.active_plugins = []
        self.commands.clear()
        self.disabled_commands.clear()
        await self.disconnect()

        for module in modules.copy():
            # Required to update helper and util file.
            if module.startswith(('userbot.helper_funcs.', 'userbot.utils.')):
                reload(modules[module])

        await self.connect()
        await event.edit(
            "`Succesfully removed all the handlers and started "
            "the client again! Adding the new handlers now. BRB..`"
        )
        self.pluginManager.import_all()
        self.pluginManager.add_handlers()

        text = "`Successfully restarted and imported all the plugins!`"
        if self.failed_imports:
            text += "\n`Failed to import:`\n"
            text += '\n'.join(self.failed_imports)
            self.failed_imports.clear()
        await event.edit(text)

        self.restarting = False
        LOGGER.info(
            "Successfully restarted and imported all the plugins! "
            "Current prefix: {}".format(self.prefix)
        )
        print()

    def _updateconfig(self):
        with open('config.ini', 'w+') as configfile:
            self.config.write(configfile)
        return True

    def _kill_running_processes(self):
        for _, process in self.running_processes.items():
            process.kill()
            LOGGER.debug("Killed %d which was still running.", process.pid)
        self.running_processes.clear()
