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


import os
import heroku3
import git
import sys
from asyncio import create_subprocess_shell, sleep

from userbot import client, LOGGER
from userbot.utils.helpers import restart

basedir = os.path.abspath(os.path.curdir)


@client.onMessage(
    command="update", info="Update the bot.",
    outgoing=True, regex="update(?: |$)(reset|add)?$"
)
async def update(event):
    arg = event.matches[0].group(1)
    main_repo = "https://github.com/kandnub/TG-UserBot.git"
    try:
        repo = git.Repo(basedir)
    except git.exc.NoSuchPathError as path:
        await event.edit(f"`Couldn't find {path}!`")
        return
    except git.exc.GitCommandError as command:
        await event.edit(
            f"`An error occured trying to get the Git Repo.`\n`{command}`"
        )
        return
    except git.exc.InvalidGitRepositoryError:
        repo = git.Repo.init(basedir)
        origin = repo.create_remote('origin', main_repo)
        if not origin.exists():
            await event.edit(
                "`The main repository does not exist. Remote is invalid!`"
            )
            return
        origin.fetch()
        repo.create_head('master', origin.refs.master).set_tracking_branch(
            origin.refs.master
        ).checkout()

    await event.edit("`Checking for updates!`")
    untracked_files = repo.untracked_files
    old_commit = repo.head.commit
    if arg == "add":
        repo.index.add(untracked_files, force=True)
        repo.index.commit("[TG-UserBot] Updater: Untracked files")
    elif arg == "reset":
        repo.head.reset('--hard')
    try:
        pull = repo.remotes.origin.pull()
    except git.exc.GitCommandError as command:
        text = (
            "`An error occured trying to Git pull:`\n`{0}`\n\n"
            "`You may use` **{1}update reset** `or` **{1}update add** "
            "`to reset your repo or add and commit your changes as well.`"
        )
        prefix = client.prefix if client.prefix is not None else '.'
        await event.edit(text.format(command, prefix))
        return
    new_commit = repo.head.commit
    if old_commit == new_commit:
        await event.edit("`Already up-to-date!`")
        return

    heroku_api_key = client.config['userbot'].get('api_key_heroku', False)
    if os.getenv("DYNO", False) and heroku_api_key:
        heroku_conn = heroku3.from_key(heroku_api_key)
        heroku_app = None
        for app in heroku_conn.apps():
            if app.name == os.getenv('HEROKU_APP_NAME', ''):
                heroku_app = app
                break
        if heroku_app is None:
            await event.edit(
                "`You seem to be running on Heroku "
                "with an invalid environment. Couldn't update the app.`\n"
                "`The changes will be reverted upon dyno restart.`"
            )
            await sleep(2)
            await updated_pip_modules(event, pull, repo, new_commit)
            await restart(event)
        else:
            # Don't update the telethon environment varaibles
            userbot_config = client.config['userbot']
            app.config().update(dict(userbot_config))
            app.config().update(
                {'userbot_restarted': f"{event.chat_id}/{event.message.id}"}
            )
            url = app.git_url.replace(
                "https://", ''.join(["https://api:", heroku_api_key, "@"])
            )
            if "heroku" in repo.remotes:
                repo.remotes['heroku'].set_url(url)
            else:
                repo.create_remote('heroku', url)
            if repo.untracked_files:
                repo.index.add(untracked_files, force=True)
                repo.index.commit("[TG-UserBot] Updater: Untracked files")
            app.enable_feature('runtime-dyno-metadata')
            await event.edit("`Pushing all the changes to the Heroku.`")
            remote = repo.remotes['heroku']
            try:
                remote.push(f'{str(repo.active_branch)}:master', '--force')
                await event.edit("`There was nothing to push to Heroku?`")
            except git.exc.GitCommandError as command:
                await event.edit(
                    "`An error occured trying to pull and push to Heorku`"
                    f"\n`{command}`"
                )
                LOGGER.exception(command)
    else:
        await updated_pip_modules(event, pull, repo, new_commit)
        await restart(event)


async def updated_pip_modules(event, pull, repo, new_commit):
    pulled = getattr(pull, str(repo.active_branch), False)
    if pulled and pulled.old_commit:
        for f in new_commit.diff(pulled.old_commit):
            if f.b_path == "requirements.txt":
                await event.edit("`Updating the requirements.`")
                await update_requirements()


async def update_requirements():
    reqs = os.path.join(basedir, "requirements.txt")
    try:
        await create_subprocess_shell(
            ' '.join(sys.executable, "-m", "pip", "install", "-r", str(reqs))
        )
    except Exception as e:
        LOGGER.exception(e)
