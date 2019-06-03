from telethon.sync import TelegramClient

# Use your own values from my.telegram.org
api_id = None
api_hash = None

if not api_id and not api_hash:
    api_id = int(input('Please enter your API ID: '))
    api_hash = input('Please enter your API Hash: ')

# The first parameter is the .session file name (absolute paths allowed)
with TelegramClient('userbot', api_id, api_hash) as client:
    client.start()