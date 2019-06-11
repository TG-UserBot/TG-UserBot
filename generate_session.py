from telethon.sync import TelegramClient

api_id = int(input('Please enter your API ID (Integers only): '))
api_hash = input('Please enter your API Hash: ')

# The first parameter is the .session file name (absolute paths allowed)
with TelegramClient('userbot', api_id, api_hash) as client:
    client.start()