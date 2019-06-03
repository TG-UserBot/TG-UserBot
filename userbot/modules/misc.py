from datetime import datetime

from userbot import client
from userbot.events import message


@message(outgoing=True, pattern='^.ping$')
async def ping(event):
    start = datetime.now()
    await event.edit("`Pong!`")
    duration = (datetime.now() - start)
    seconds = duration.seconds
    milliseconds = duration.microseconds / 1000
    await event.edit(f"`{milliseconds}ms | {seconds}s`")


@message(outgoing=True, pattern='^.disconnect$')
async def disconnect(event):
    await event.edit("`Ciao!`")
    await client.disconnect()