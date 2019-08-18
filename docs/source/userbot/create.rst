.. _create:

=================
Creating commands
=================

To create a command you need to make an async function with a Pyrogram
decorator in an individual or an already existing file in the
``TG-UserBot/userbot/plugins/`` directory. Pyrogram will load the this
manually if you use Pyrogram's decorators, else they won't be reloaded
on a restart.


.. contents::


Examples
--------
The events module already has Filters and on_message decorator imported
in it so you can import them from their instead of pyrogram. The commands
decorator is used to store a command with it's function's handler so it
can be used to disable/enable it later via the main commands.


To create function which replies to all your texts with the text you sent.
For instance, you say "xyz", it will reply to your text with
"You said *xyz*!"

.. code-block:: python

    from userbot.events import commands, Filters, on_message

    @commands("echo")
    @on_message(Filters.me & Filters.text)
    async def echo(client, event):
        text = "You said __{}__!".format(event.text)
        await event.reply(text)


To create function which edits your "hi" text to a "hello".

.. code-block:: python

    from userbot.events import commands, Filters, on_message

    @commands("hi")
    @on_message(Filters.me & Filters.regex("(?i)^hi$")
    async def hello(client, event):
        await event.edit("hello")
