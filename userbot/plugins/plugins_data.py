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


import base64
import dataclasses
import dill
import os


def load_data(name: str) -> dict:
    b64 = os.environ.pop(name, {})
    if b64:
        b64 = dill.loads(base64.b64decode(b64.encode()))
    return b64


def dump_data(instance) -> dict:
    data_dict = {}
    for i in dataclasses.fields(instance):
        attr = getattr(instance, i.name, None)
        if attr:
            data_dict[i.name] = base64.b64encode(dill.dumps(attr)).decode()
    return data_dict


@dataclasses.dataclass
class AFK:
    privates: dict = None
    groups: dict = None
    sent: dict = None


def dump_AFK() -> None:
    cls_dict = dump_data(AFK)
    if "privates" in cls_dict:
        os.environ['userbot_afk_privates'] = cls_dict['privates']
    if "groups" in cls_dict:
        os.environ['userbot_afk_groups'] = cls_dict['groups']
    if "sent" in cls_dict:
        os.environ['userbot_afk_sent'] = cls_dict['sent']


@dataclasses.dataclass
class Blacklist:
    bio: list = None
    url: list = None
    tgid: list = None
    txt: list = None


@dataclasses.dataclass
class GlobalBlacklist:
    bio: list = None
    url: list = None
    tgid: list = None
    txt: list = None
