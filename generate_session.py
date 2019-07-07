from asyncio import get_event_loop
from configparser import ConfigParser
from os.path import isfile
from sys import exit

from pyrogram import Client


if not isfile('config.ini'):
    print("Please make sure you have a config.")
    exit(1)

client = Client("userbot")

configparser = ConfigParser()
configparser.read('config.ini')
api_id = configparser['pyrogram'].getint('api_id', 0)
api_hash = configparser['pyrogram'].get('api_hash', None)

if not api_id:
    print("Please make sure you have set your API ID in config.")
    exit(1)
elif not api_hash:
    print("Please make sure you have set your API hash in config.")
    exit(1)


async def main():
    await client.start()
    await client.stop()


loop = get_event_loop()
loop.run_until_complete(main())