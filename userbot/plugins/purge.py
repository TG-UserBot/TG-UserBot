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


from asyncio import sleep

from userbot import client


@client.onMessage(
    command="purge", info="Purge multiple messages!",
    outgoing=True, regex=r"purge(?: |$)(\d*)", require_admin=True
)
async def purge(event):
    if (
        (event.is_channel or event.is_group) and
        not (event.chat.creator or event.chat.admin_rights.delete_messages)
    ):
        await event.edit("`You do not have message deleting rights in here!`")
        return

    entity = await event.get_input_chat()
    amount = event.matches[0].group(1)
    reverse = False
    limit = None

    if event.reply_to_msg_id:
        await event.delete()
        offset = await event.get_reply_message()
        reverse = True
        if amount:
            limit = int(amount) - 1
    elif amount:
        offset = event
        limit = int(amount)
    else:
        await event.edit("`Purge yourself!`")
        await sleep(2)
        await event.delete()
        return

    messages = [offset.id]
    async for msg in client.iter_messages(
        entity=entity,
        offset_id=offset.id,
        reverse=reverse,
        limit=limit
    ):
        messages.append(msg.id)

    await client.delete_messages(entity, messages)
    toast = await event.respond(
        f"`Successfully deleted {len(messages)} messages!`"
    )
    await sleep(2)
    await toast.delete()


@client.onMessage(
    command="delme", info="Delete YOUR messsages!",
    outgoing=True, regex=r"delme(?: |$)(\d*)"
)
async def delme(event):
    entity = await event.get_input_chat()
    amount = event.matches[0].group(1)
    offset = 0
    reverse = False
    limit = None
    reply_message = None

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        await event.delete()
        if reply.sender_id == (await client.get_me()).id:
            reply_message = reply.id
        offset = reply.id
        reverse = True
        if amount:
            limit = int(amount)
    elif amount:
        await event.delete()
        offset = event.id
        limit = int(amount)
    else:
        await event.delete()
        offset = event.id
        limit = 1

    messages = []
    if reply_message:
        messages.append(reply_message)

    async for msg in client.iter_messages(
        entity=entity,
        offset_id=offset,
        reverse=reverse,
        limit=limit,
        from_user="me"
    ):
        messages.append(msg.id)

    await client.delete_messages(entity, messages)
    toast = await event.respond(
        f"`Successfully deleted {len(messages)} messages!`"
    )
    await sleep(2)
    await toast.delete()
