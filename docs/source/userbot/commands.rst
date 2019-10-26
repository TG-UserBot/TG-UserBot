.. _commands:

===================
Available Commands
===================

Here you can find all the commands available in the UserBot including their
description, how to use them correctly and what they return.


.. note::
    ``.`` is the prefix used on here but you can also use ``/``, ``#``, etc.
    by setting with with ``<prefix>setprefix <newprefix>``. For instance:
    ``.setprefix /`` changes ``.`` to ``/``.


.. contents::


-------------
Main Commands
-------------

Commands
--------
Lists all the enabled bot commands.

**Usage:** ``.commands``

**Returns:** A list of all the enabled bot commands.


Disable
-------
Disable any bot command with it's name. Restarting will enable all the
disabled commands.

**Usage:** ``.disable sed``

**Returns:** This disables the use of sed by removing it's handler.

Disabled
--------
Lists all the disabled bot commands.

**Usage:** ``.disabled``

**Returns:** A list of all the disabled bot commands.


Enable
------
Enable any disabled bot commands with it's name.

**Usage:** ``.enable sed``

**Returns:** This enables the sed command if it was disabled.

Restart
-------
Restarts the Telethon client. This reloads all the modules (smart plugins)
with it.

**Usage:** ``.restart``


Set Prefix
----------
Change the default prefix for all the commands.

**Usage:** ``.setprefix !``

**Returns:** The new prefix and how to reset to old prefix.

Reset Prefix
------------
Resets to the default prefix which is ".".

**Usage:** ``resetprefix``

**Note:** "resetprefix" works without any prefix because it is a fail-safe
incase the user forgets the prefix.


Shutdown
--------
Stops the Telethon client and exits the main script completely.

**Usage:** ``.shutdown``


-------------
Bot Commands
-------------

Dismiss
-------
Unpin the `Saved Messages` dialog.

**Usage:** ``dismiss``

**Returns:** Unpins `Saved Messages` dialog and deletes the replied to message
if any.


Remind me
---------
Set a reminder for yourself.

**Usage:** ``.remindme 2h Go outside`` *Format: .remindme time text*

    Available time units: `w, d, h, m, s`.

**Returns:** This will send `Go outside` to your `Saved Messages` after 2 hours
and pin the dialog.


Eval
----
Evaluates the provided code.

**Usage:** ``.eval 60+9`` or ``.eval reply``

**Returns:** `69` or the `Message` object of the replied message.


Exec
----
Executes the provided Python code.

**Usage:** ``.exec print("TG-UserBot")``

**Returns:** `TG-UserBot`.


Get sticker
-----------
Convert a sticker to a png format.

**Usage:** ``.getsticker`` or ``.getsticker file`` or ``.getsticker document``

**Returns:** Get replied to sticker as an image or as a file if mentioned.


Nearest DC
----------
Get your country, current DC and nearest DC information of account.

**Usage:** ``.nearestdc``

**Returns:** Country, your current DC and nearest DC.


Ping
----
Message edit/send response time.

**Usage:** ``.ping``

**Returns:** The time it took to edit the message.


Ping DC
-------
Gets the average response time of a datacenter (DC).

**Usage:** ``.pingdc`` or ``.pingdc n`` *n refers to the DC (1 - 5)*

**Returns:** Average response time of your DC or the one you specified.


Regex Ninja
-----------
Automatically deletes sed commands for regexbot.

**Usage:** ``regexninja on`` or ``regexninja off`` or
``regexninja``

    * on or off are used to set the mode. Without it, it'll return the current
      value.

**Returns:** New or current mode for Regex Ninja.


SED
---
Perform a regular expression substituion with the provided replacement.

**Usage:** ``s/hi/hello`` or ``2s/cat/dog; s|boi|boy`` or
``s\crack\dope\g; 6s/cow/horse/i`` *Format: ns/regexp/replacement/flags;*

    * `n` refers to a line.
    * The line and flags are optional.
    * Use your delimeter or a semicolon to end each substituion for multiple
      replacement.

**Returns:** The replaced text if it there was successful match. If there was
no replied to messages, then the last 10 messages will be used as source and
the one which has a match will be used for replacement.


Term
----
Executes terminal commands.

**Usage:** ``.term ls``

**Returns:** The result of `ls` command.


YouTube-DL
----------
Download videos from supported sites in your choice of format.

**Usage:** ``.yt_dl https://youtu.be/dWhyFfsb74g listformats``
or ``.yt_dl https://youtu.be/dWhyFfsb74g bestaudio+bestvideo``
*Format: .yt_dl url format*

    Have a look at YouTube-DL's `format selection`_ for more information
    on formats and merging.

**Returns:** All the available formats or downloads the specified video's best
audio and video, then merges them together.


.. _format selection: https://github.com/ytdl-org/youtube-dl#format-selection
