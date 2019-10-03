.. _commands:


===================
Available Commands
===================

You will find all the commands available in the UserBot including their
description, how to use them correctly and what they return.


.. note::
    ``.`` is the prefix used on here but you can also use ``/``, ``#``, etc.
    by setting with with ``<prefix>setprefix <newprefix>``. For instance:
    ``.setprefix /`` changes ``.`` to ``/``.


.. contents::


-------------
Main Commands
-------------

Commands (*commands*)
---------------------
Lists all the enabled bot commands.

**Usage:** ``.commands``

**Returns:** A list of all the enabled bot commands.


Set Prefix (*setprefix*)
------------------------
Change the default prefix for all the commands.

**Usage:** ``.setprefix !``

**Returns:** The new prefix and how to reset to old prefix.


Disable (*disable*)
-------------------
Disable any bot command with it's name. Restarting will enable all the
disabled commands.

**Usage:** ``.disable sed``

**Returns:** This disables the use of sed by removing it's handler.


Disabled (*disabled*)
---------------------
Lists all the disabled bot commands.

**Usage:** ``.disabled``

**Returns:** A list of all the disabled bot commands.


Enable (*enable*)
-------------------
Enable any disabled bot commands with it's name.

**Usage:** ``.enable sed``

**Returns:** This enables the sed command if it was disabled.


Restart (*restart*)
-------------------
Restarts the Telethon client. This reloads all the modules (smart plugins)
with it.

**Usage:** ``.restart``


Shutdown (*shutdown*)
---------------------
Stops the Telethon client and exits the main script completely.

**Usage:** ``.shutdown``


-------------
Bot Commands
-------------

Eval (*eval*)
-------------
Evaluates the provided code.

**Usage:** ``.eval 60+9`` or ``.eval reply``

**Returns:** `69` or the `Message` object of the replied message.


Exec (*exec*)
-------------
Executes the provided Python code.

**Usage:** ``.exec print("TG-UserBot")``

**Returns:** `TG-UserBot`.


Term (*term*)
-------------
Executes terminal commands.

**Usage:** ``.term ls``

**Returns:** The result of `ls` command.


Ping (*ping*)
-------------
Message edit/send response time.

**Usage:** ``.ping``

**Returns:** The time it took to edit the message.


Ping DC (*pingdc*)
------------------
Gets the average response time of a datacenter (DC).

**Usage:** ``.pingdc`` or ``.pingdc n`` *n refers to the DC (1 - 5)*

**Returns:** Average response time of your DC or the one you specified.


Remind me (*remindme*)
----------------------
Set a reminder for yourself.

**Usage:** ``.remindme 2h Go outside`` *Format: .remindme time text*

    Available time units: `w, d, h, m, s`.

**Returns:** This will send `Go outside` to your `Saved Messages` after 2 hours
and pin the dialog.


Dismiss (*dismiss*)
-------------------
Unpin the `Saved Messages` dialog.

**Usage:** ``dismiss``

**Returns:** Unpins `Saved Messages` dialog and deletes the replied to message
if any.


SED (*sed*)
-----------
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


Regex Ninja (*regexninja*)
--------------------------
Automatically deletes sed commands for regexbot.

**Usage:** ``regexninja on`` or ``regexninja off`` or
``regexninja``

    * on or off are used to set the mode. Without it, it'll return the current
      value.

**Returns:** New or current mode for Regex Ninja.


Get sticker (*getsticker*)
--------------------------
Convert a sticker to a png format.

**Usage:** ``.getsticker``

**Returns:** Sends the replied to sticker in a png format.


Nearest DC (*nearestdc*)
------------------------
Get your current DC, nearest DC and country information of account.

**Usage:** ``.nearestdc``

**Returns:** Your current DC, nearest DC and current country.


YouTube-DL (*yt_dl*)
--------------------
Download videos from supported sites in your choice of format.

**Usage:** ``.yt_dl https://youtu.be/dWhyFfsb74g listformats``
or ``.yt_dl https://youtu.be/dWhyFfsb74g bestaudio+bestvideo``
*Format: .yt_dl url format*

    Have a look at YouTube-DL's `format selection`_ for more information
    on formats and merging.

**Returns:** All the available formats or downloads the specified video's best
audio and video, then merges them together.


.. _format selection: https://github.com/ytdl-org/youtube-dl#format-selection
