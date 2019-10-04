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


from logging import StreamHandler

from userbot import (
    __copyright__, __license__,
    client, ROOT_LOGGER, verifyLoggerGroup
)
from userbot.helper_funcs.log_formatter import CustomFormatter
from userbot.utils.helpers import printUser, printVersion
from userbot.utils.pluginManager import PluginManager


handler = StreamHandler()

handler.setFormatter(CustomFormatter())
ROOT_LOGGER.addHandler(handler)

print(__copyright__)
print("Licensed under the terms of the " + __license__)


if __name__ == "__main__":
    client.pluginManager = PluginManager(client)
    client.pluginManager.import_all()
    client.pluginManager.add_handlers()
    client.start()

    verifyLoggerGroup(client)
    printUser(client.loop.run_until_complete(client.get_me()))
    printVersion(client.version, client.prefix)

    client.run_until_disconnected()
