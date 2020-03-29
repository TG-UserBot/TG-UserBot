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

Help
--------
Lists all the enabled bot commands.

**Usage:** ``.help [all|category|command (dev)]``

**Returns:** ``all`` returns a list of all the enabled userbot commands. ``category`` returns the commands from the mentioned category.
``command (dev)`` returns the help for the mentioned command, here ``dev`` is optional and when mentioned it returns developer info for that
command 


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

Enabled
-------
Lists all the enabled commands.

**Usage:** ``.enabled``

**Returns:** This returns a list of all enabled

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

AFK
---
Set your status as afk.

**Usage:** ``.afk (reason)``

**Returns:** If anyone mentions/tags you, the userbot will notify them that you are afk for whatever
reason if mentioned.

Approve
------------
Approve a user for them to PM you.

**Usage:** ``.approve @username/reply to a message``

Approved
---------
Returns a list of all approved users
**Usage:** ``.approved``

Ban
------------
Bans the user from a channel or chat with reason if mentioned.

**Usage:** ``.ban @username/user-id/reply to a message (reason)``

**Example:** *.ban @shxnpie too goldy to handle*

    This will ban @shxnpie with the reason "too godly to handle"

Bio
------------
View or change your bio.

**Usage:** ``.bio (text)``

**Returns:** If nothing is mentioned the bot will show your current bio and 
if some text is mentioned it will changed your bio to the same.

Bird
------------
Send a pic of a random bird.

**Usage:** ``.bird``

Blacklist
------------
Add an item to the userbot's blacklist.

**Usage:** ``.(g)bl <value1>..<valuen> or <option>:<value>``

    Here "g" stands for global. bl is chat specific while gbl is global
    
    Options/Values: user-id, Bio strings, text strings, domain/url

**Example:** *.gbl 1007684893 863314639* or 
*.bl id:863314639 url:https://www.google.com str:kan bad*

**Returns:** This will (g)ban the user if they match with the blacklisted items.

Blacklisted
------------
Shows a list of all blacklisted users

**Usage:** ``.blacklisted``

Blacklists
------------
Sends a list of all blacklisted items

**Usage:** ``.blacklist``

Block
------------
Block a User.

**Usage:** ``.block @username/user-id``

Cat
----
Send a random image of a cat.

**Usage:** ``.cat``

Covid
---
Send info about the Covid-19 Pandemic.

**Usage:** ``.covid (country)``

**Returns:** If a country is mentioned it will give  its stats or World's stats will be shown.

Delete 
------------
Deletes the tagged message.

**Usage:** ``.del`` in reply to a message.

Delete Me
------------
Deletes your message.

**Usage:** ``.delme (n)`` if the number of message is not mentioned it will delete the message above it.

Delete Profile Picture
----------------------
Deletes your profile picture a.k.a pfp

**Usage:** ``.delpfp (n)`` If numberof pfp is not mentioned it will delete the current pfp.

Delete Sticker
--------------
Deletes the tagged sticker from your sticker pack

**Usage:** ``.delsticker`` in reply to a sticker in your pack.

Demote
------------
Demotes an admin to a user.

**Usage:** ``.demote @username/user-id``

Download
------------
Download a file from TG to the local storage

**Usage:** ``.dl`` in reply to a file/sticker

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

User/Chat/Channel ID 
----------------------
Shows the user/chat/channel's id.

**Usage:** ``.id (@username)`` if nothing is mentioned it will give the chat's id.

Kang
-----
Kang a sticker and add it to your pack.

**Usage:** ``.kang`` if the command is not in reply to a sticker, the bot will kang the nearest available sticker.

Kick
------------
Kick a user form a chat/channel

**Usage:** ``.kick @username (reason)`` reason is optional

Kill
------------
Kill a sub-process

**Usage:** ``.kill`` in reply to .eval or .exec sub-processes

Mention
------------
Mention a user without the @

**Usage:** ``@Username[text]`` 

**Returns:** This will tag the user within the text.

Mute
------------
Mute a user.

**Usage:** ``.mute @username (reason)`` reason is optional

Name
------------
Show/Change your name

**Usage:** ``.name (text)``

**Returns:** Shows your current name and changes it if a textis specified.

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

Profile Picture
---------------
Show/Change profile picture.

**Usage:** ``.pfp`` in reply to an image, if not replied it will show your current pfp.

Promote
------------
Promote a user to an admin.

**Usage:** ``.promote @username (title="some text")``

**Returns:** This will promote the user. Title is optional.

Purge
------------
Purge or delete messages.

**Usage:** ``.purge (n) or reply to a message.``

**Returns:** This will purge the *n* number of messages or if replied to a messaged it will
purge that message and all the messages below it.

Regex Ninja
-----------
Automatically deletes sed commands for regexbot.

**Usage:** ``regexninja on`` or ``regexninja off`` or
``regexninja``

    * on or off are used to set the mode. Without it, it'll return the current
      value.

**Returns:** New or current mode for Regex Ninja.

Remind Here
------------
Send you a reminder in the current chat

**Usage:** ``.remindhere w,d,h,m,s reply to a text or reason``
 
    Available time units: `w, d, h, m, s`.

Remind me
---------
Set a reminder for yourself.

**Usage:** ``.remindme w,d,h,m,s reply to a text or reason``

    Available time units: `w, d, h, m, s`.

Repository
------------
Send a URL of the repository.

**Usage:** ``.repo``

Resolve
------------
Resolve a username/user-id/channel invites

**Usage:** ``.resolve username/user-id/channel invites``

**Returns:** This returns with the info of the specified item.

Reverse
------------
Do a reverse image search on google.

**Usage:** ``.reverse`` in reply to an image

**Returns:** With similar looking images and a possible related search term.

Remove Background
-----------------------
Removes the background from an image. (Requires `Remove.bg`_ API Key)

**Usage:** ``.rmbg`` in reply to an image

Remove blacklist
-----------------------
Remove a blacklisted id/string/url.

**Usage:** ``rmblacklist id/string/url``

Remove Whitelist
-----------------------
Removes the user form whitelist.

**Usage:** ``rmwhitelist id``

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


Shiba Inu
------------
Sends a random image of Shiba Inus

**Usage:** ``.shibe``

Speedtest
------------
Perform a Speedtest.

**Usage:** ``.speedtest``

Stciker Pack(s)
-----------------------
Show a list of all of your sticker packs

**Usage:** ``.stickerpack``

Temporary Ban
------------------
Temp ban an user.

**Usage:** ``.tban``

Term
----
Executes terminal commands.

**Usage:** ``.term ls``

**Returns:** The result of `ls` command.

Terminate
------------
Terminate or kill a sub-process
**Usage:** ``.terminate`` in reply to .eval or .exec sub-processes.

Temporary Mute
-----------------------
Temp mute an user
**Usage:** ``.tmute``

Un/Dis Approve
-----------------------
Un Approve someone from PM-ing you.

**Usage:** ``.unapprove @username/reply to thier message``

Unban
------------
Unban someone from a chat or channel.

**Usage:** ``.unban @username/reply to thier message``

Un Blacklist
------------
Remove an user from blacklist.

**Usage:** ``.unblacklist user-id``

Un Mute
------------
Un Mute an user.

**Usage:** ``.unmute @username/reply to thier message``

Update
------------
Update the userbot

**Usage:** ``.update``

**Returns:** This will pull latest changes from the repo and update the bot.

    Heroku users need Heroku API ID for update to work.

Upload
------------
Upload local files to Telegram.

**Usage:** ``.upload path to file``

Username
------------
View/Change ypur username.

**Usage:** ``.username (text)`` if text is not mentioned it will show your username.

Whitelist
------------
Whitelist an user.

**Usage:** ``.whitelist user-id``

Whitelists
------------
Show a list of all whitelisted users.

**Usage:** ``.whitelists``

Who is
------------
Give all info about an user or a chat.

**Usage:** ``.whois @username/reply to a message/this``

    .whois this returns info about the chat.

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
.. _Remove.bg: https://www.remove.bg/
