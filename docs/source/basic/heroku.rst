.. _heroku guide:
.. role:: raw-html(raw)
    :format: html



=============
Heroku Guide
=============

.. note::
    This guide only shows how to generate a Redis session and deploy the bot to `Heroku`_.

We would encourange you to use Termux, an app available on the Play Store.
Open the same and follow along. 

.. contents::

Prerequesites
-------------
- API ID and Hash from `Telegram`_
- Redis Endpoint and Password from Redis Labs:

  - Get the 30MB free Database from `Redis Labs`_

Cloning the repository
----------------------
Clone the `TG-UserBot repository`_ to your desired location
using the `git clone` command.

.. code:: sh

    $ git clone https://www.github.com/kandnub/TG-UserBot

Once the cloning has finished, change your directory to the
cloned folders directory using the `cd` command.

.. code:: sh

    $ cd TG-UserBot


Installing Redis and Telethon
-----------------------------

.. code:: sh

    $ pip install redis telethon


Generating a Redis Session
--------------------------
To generate the session do: 

.. code:: sh

    $ python3 generate_session.python3


Simply follow the on-screen instructions and you'll get a confirmation message saying:

    Succesfully generated a session for "name"

Depolying to Heroku
-------------------

To deploy to heroku click on the Auto Deploy button given below:

.. image:: ../_images/heroku.png
    :width: 220px
    :align: center
    :height: 50px
    :target: https://heroku.com/deploy?template=https://github.com/kandnub/TG-UserBot


Fill all the info i.e ENV Vars, double check and click on deploy, thats it you are done! :raw-html:`<br />`
If you get stuck somewhere or get an error while building/deploying the UserBot, don't hesitate to ask us in
the `support group`_.

.. _Heroku: https://www.heroku.com
.. _Telegram: https://my.telegram.org/apps
.. _TG-UserBot repository: https://www.github.com/kandnub/TG-UserBot
.. _Redis Labs: https://redislabs.com/
.. _support group: https://t.me/tg_userbot_support

