# TG-UserBot

A modular Telegram UserBot for Python which uses the [Telethon][telethon] library. It is made to help you do your usual client tasks without the hassle and also has some additional useful features.

### Requirements

- Python 3.7 or above.
- A Telegram [API key][tg-apps] (API ID and hash).

### Procedure

Clone the repository.

```sh
$ git clone https://github.com/kandnub/TG-UserBot/
```

Change the current directory to the cloned one.

```sh
$ cd TG-UserBot
```

Edit the ``sample_config.ini`` with your API key, save it and rename it to ``config.ini``.
You can use nano/vim or do it manually using a text editor.

```sh
$ nano sample_config.ini
$ mv sample_config.ini config.ini
```

Install all the requirements using pip.

```sh
$ pip3 install --user -r requirements.txt
```

Run the UserBot once you have a valid configuration file.

```sh
$ python3 -m userbot
```

### Resources

- View the [TG-UserBot documentation][docs] if you're stuck somewhere or need to find something.
- Join the [Telegram support group][support] if you have any issues or feedback that you'd like to share.

### Contributing

Either submit pull requests or create an issue on here, if not, you can join the support group and let us know. Module/command requests or ways to improve the current code is also appreciated.

### Copyright & License

- Copyright (C) 2019 Kandarp <<https://github.com/kandnub>>
- Licensed under the terms of the [GNU General Public License v3.0 or later (GPLv3+)](LICENSE)

[//]: # (Comment)
   [pyrogram]: <https://github.com/LonamiWebs/Telethon/>
   [tg-apps]: <https://my.telegram.org/apps>
   [docs]: <https://tg-userbot.readthedocs.io>
   [support]: <https://t.me/tg_userbot_support>