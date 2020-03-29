==========================
TG-UserBot's Documentation
==========================


What is this?
-------------
**TG-UserBot** is a modular Python script for Telegram_ which uses the
Telethon_ library. It is made to help you do your usual client tasks without
the hassle and also has some additional useful features. If a command is
documented, it will be on the :doc:`Available commands<userbot/commands>` page
including it's description with an example if any.


Prerequisites?
--------------
* Python_ 3.7.3 or above.
* Git_.
* Telegram API key (API ID and hash) from https://my.telegram.org/apps.
* FFMPEG_ (optional) for YouTube-DL_. Guide covers this requirement.
* Some basic understanding would also be helpful.


Where to look?
--------------
Everything is self-contained into it's own catergory and can be accessed
from the sidebar or by using the :guilabel:`Previous` or :guilabel:`Next`
buttons at the end of the page. Main topics are listed below accordingly.

* :doc:`Beginners guide<basic/preparation>`: A follow along guide to
  set-up everything correctly.
* :doc:`Available commands<userbot/commands>`: All the available UserBot
  commands will be listed on this page.
* :doc:`FAQ<faq>`: Most commonly asked questions will
  be answered on here, hopefully you find what you're looking for on here.

**Looking for the details on the code itself?**

* :doc:`Modules<userbot/plugins>`: All the modules (smart plugins) and
  their functions can be found here with their descriptions.
* :doc:`Helper functions<userbot/helper_funcs>`: All the functions used
  to reduce bloat in multiple modules can be found here with their examples.
* :doc:`Utilities<userbot/utils>`: Utilities used to keep the bot organized
  and clean.
* :doc:`Creating your own command<userbot/create>`: Examples to create your
  own commands can be found here.

If you want to report an issue, have any feedbacks/suggestions or want to
discuss something then you may join the `support group`_ on Telegram.


.. _FFMPEG: https://www.ffmpeg.org
.. _Git: https://git-scm.com
.. _Telethon: https://telethon.readthedocs.io/en/latest/
.. _Python: https://www.python.org
.. _support group: https://t.me/tg_userbot_support
.. _Telegram: https://telegram.org
.. _YouTube-DL: https://github.com/ytdl-org/youtube-dl


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: First Steps

   basic/preparation
   faq

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Heroku

   basic/heroku

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: UserBot

   userbot/commands
   userbot/plugins
   userbot/helper_funcs
   userbot/utils
   userbot/create
