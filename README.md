# TG-UserBot

A modular Telegram UserBot for Python which uses the [Telethon][telethon] library. It is made to help you do your usual client tasks without the hassle and also has some additional useful features.

[![Documentation Status][docsbadge]][docs]
# 

## Heroku guide is available [here][heroku-guide].
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)][heroku-deploy]


``Incase your Redis session renders invalid, stop your dyno & run the userbot locally again, it will delete your old session from Redis. Then re-run the userbot again, login and exit it and start your dyno on Heroku.``

# 

## Requirements:

- Python 3.7.3 or above.
- A Telegram [API key][tg-apps] (API ID and hash).
- Redis Endpoint and Password from [Redis Labs][redis]
   - Redis session is optional but needed if you are planning to use AFK and PM-Permit.

## Procedure:

Clone the repository.

```sh
$ git clone https://github.com/kandnub/TG-UserBot/
```

Change the current directory to the cloned one.

```sh
$ cd TG-UserBot
```

Edit the config either using Nano/Vim or a Text Editor and put your ENV Vars in the same.
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
# 
## Resources:

- [TG-UserBot Documentations][docs]: Official userbot documentations. Here you can find all the help you need to get the bot up and running and can also find all the documented commands.
   - Regular maintenance of docs is not possible thus some new commands may be missing from the same.
- [Telegram Support Group][support]: Exclusive Telegram support group. On here you can ask for help, request a feature or provide feedback to improve the bot.Constructuive criticism is also appriciated



## Contributing:

Either submit pull requests or create an issue on here.

## Copyright & License

- Copyright (C) 2020 [Kandarp](https://github.com/kandnub).
- Licensed under the terms of the [GNU General Public License v3.0 or later (GPLv3+)](LICENSE).

[//]: # (Comment)
   [telethon]: <https://github.com/LonamiWebs/Telethon/>
   [tg-apps]: <https://my.telegram.org/apps>
   [docs]: <https://tg-userbot.readthedocs.io/en/latest/>
   [docsbadge]: <https://readthedocs.org/projects/tg-userbot/badge/?version=latest>
   [support]: <https://t.me/tg_userbot_support>
   [redis]: <https://redislabs.com>
   [heroku-deploy]: <https://heroku.com/deploy?template=https://github.com/kandnub/TG-UserBot>
   [heroku-guide]: <https://tg-userbot.readthedocs.io/en/latest/basic/heroku.html>
