.. _preparations:


===================
How to get started
===================

.. warning::
   This will not cover the installation of Python or Git.

Assuming you (already) have Python and Git installed,
you can go ahead and follow along.

.. contents::


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


Configuration file
------------------
Now you need configure the ``sample_config.ini`` with your API ID
and hash using your preferred text editor, these are mandatory fields.
You may leave the rest as they are or change them to your liking. Once
done, rename ``sample_config.ini`` to ``config.ini`` and proceed.

.. code:: sh

    $ nano sample_config.ini
    $ mv sample_config.ini config.ini


Installing requirements
-----------------------
The main part has been done, now you only need to install all the requirements
with the `pip install` command, this may take a while to finish. Make sure you
execute this command in the cloned directory. If you want to install FFMPEG_
then have a look at the FAQ's :ref:`How to install FFMPEG?<faq>` answer before
proceeding any further.

.. code:: sh

    $ pip3 install -r requirements.txt


Generating a session
--------------------
.. note::
    You will need to enter your phone number and enter the recieved
    verification code in terminal to login.

    If the code is correct and it doesn't work (invalid) then Telegram
    has detected the code being sent to others. There's nothing you
    can do about this so try again later.

    If there's an existing ``userbot.session`` in the directory,
    script will exit to prevent logging in using that
    (terminated / corrupted) session.

Now that you have a proper configuration and all the requirements installed.
You need to generate a session in order to connect to Telegram and run the
UserBot script.

.. code:: sh

    $ python3 generate_session.py


Running the UserBot
-------------------
That's it. You're all done with the jarring work, you can now run the main
UserBot script without any worries. If you encounter any problem, consider
reffering to the FAQ's page or join the `support group`_.

.. code:: sh

    $ python3 -m userbot



.. _FFMPEG: https://www.ffmpeg.org
.. _support group: https://t.me/tg_userbot_support
.. _TG-UserBot repository: https://www.github.com/kandnub/TG-UserBot
