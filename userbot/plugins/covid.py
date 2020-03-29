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


from covid import Covid

from userbot import client
from userbot.utils.events import NewMessage


plugin_category = "pandemic"
covid_str = f"""`{'Confirmed':<9}:`  **%(confirmed)s**
`{'Active':<9}:`  **%(active)s**
`{'Recovered':<9}:`  **%(recovered)s**
`{'Deaths':<9}:`  **%(deaths)s**"""
critical_str = f"\n`{'Critical':<9}:`  **%(critical)s**"


@client.onMessage(
    command="covid",
    outgoing=True, regex="(?:covid|corona)(?: |$)(.*)"
)
async def covid19(event: NewMessage.Event) -> None:
    """Get the current COVID-19 stats for a specific country or overall."""
    covid = Covid(source="worldometers")
    match = event.matches[0].group(1)
    if match:
        strings = []
        failed = []
        args, _ = await client.parse_arguments(match)
        if match.lower() == "countries":
            strings = sorted(covid.list_countries())
        else:
            for c in args:
                try:
                    country = covid.get_status_by_country_name(c)
                    string = f"**COVID-19** __({country['country']})__\n"
                    string += covid_str % country
                    if country['critical']:
                        string += critical_str % country
                    strings.append(string)
                except ValueError:
                    failed.append(c)
                    continue
        if strings:
            await event.answer('\n\n'.join(strings))
        if failed:
            string = "`Couldn't find the following countries:` "
            string += ', '.join([f'`{x}`' for x in failed])
            await event.answer(string, reply=True)
    else:
        active = covid.get_total_active_cases()
        confirmed = covid.get_total_confirmed_cases()
        recovered = covid.get_total_recovered()
        deaths = covid.get_total_deaths()
        string = f"**COVID-19** __(Worldwide)__\n"
        string += covid_str % {
            'active': active, 'confirmed': confirmed,
            'recovered': recovered, 'deaths': deaths
        }
        await event.answer(string)
