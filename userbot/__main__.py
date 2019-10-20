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


from logging import StreamHandler, getLogger
from sys import platform

import userbot
import userbot.helper_funcs.log_formatter as log_formatter
import userbot.utils.pluginManager as pluginManager
import userbot.utils.helpers as helpers

client = userbot.client
handler = StreamHandler()
LOGGER = getLogger('userbot')

handler.setFormatter(log_formatter.CustomFormatter())
userbot.ROOT_LOGGER.addHandler(handler)

print(userbot.__copyright__)
print("Licensed under the terms of the " + userbot.__license__)


async def _run_until_complete():
    await client.disconnected
    while client.restarting:
        await client.start()
        await client.disconnected
    client._kill_running_processes()


def wakeup():
    client.loop.call_later(0.1, wakeup)


if __name__ == "__main__":
    client.register_commands = True
    client.pluginManager = pluginManager.PluginManager(client)
    client.pluginManager.import_all()
    client.pluginManager.add_handlers()
    client.start()

    userbot.verifyLoggerGroup(client)
    helpers.printUser(
        client.loop.run_until_complete(client.get_me())
    )
    helpers.printVersion(client.version, client.prefix)
    client.loop.create_task(helpers.isRestart(client))

    try:
        if platform.startswith('win'):
            client.loop.call_later(0.1, wakeup)  # Needed for SIGINT handling
        client.loop.run_until_complete(_run_until_complete())
    except NotImplementedError:
        pass
    except KeyboardInterrupt:
        print()
        LOGGER.info("Exiting the script due to keyboard interruption.")
        client._kill_running_processes()
        pass
    finally:
        client.disconnect()
