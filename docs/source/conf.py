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
import sys
import sphinx_rtd_theme  # noqa: F401
from time import strftime

sys.path.insert(0, os.path.abspath('../..'))

from userbot import __version__  # noqa: E402

project = 'TG-UserBot'
copyright = '2019, Kandarp'
author = 'Kandarp'

version = __version__
release = 'stable'

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme"
]

exclude_patterns = [
    '*generate_session.py'
]

autosummary_generate = True
napoleon_use_rtype = False
pygments_style = "stata-dark"
pagename = "TG-UserBot Documentation"
html_title = "TG-UserBot Documentation"
html_short_title = "TG-UserBot"
html_show_sourcelink = True
html_show_sphinx = False
html_show_copyright = False
html_theme = "sphinx_rtd_theme"
html_logo = "_images/logo.svg"
html_favicon = "_images/favicon.ico"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_style = "css/lights_out.css"
templates_path = ['_templates']
html_static_path = ['_static']
show_authors = True


intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pyrogram': ('https://docs.pyrogram.org/dev/', None)
}

autodoc_default_options = {
    'member-order': 'bysource',
    'undoc-members': True,
    'show-inheritance': True,
    'exclude-members': '__init__',
    'ignore-module-all': True
}

html_theme_options = {
    'canonical_url': '',
    'logo_only': False,
    'display_version': True,
    'collapse_navigation': True,
    'sticky_navigation': True,
    'style_external_links': False,
    'style_nav_header_background': '#EF3449'
}

html_context = {
    # Our last updated format.
    'l_updated': strftime('%b %d, %Y'),
    # Enable the "Edit in GitHub link within the header of each page.
    'display_github': True,
    'github_user': 'kandnub',
    'github_repo': 'TG-UserBot',
    'github_version': 'master',
    'conf_py_path': '/docs/source/'
}


def setup(app):
    app.add_stylesheet("css/lights_out.css")
