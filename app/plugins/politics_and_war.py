# This is part of Requiem
# Copyright (C) 2020  God Empress Verin

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import datetime
import aiohttp
import logging
import discord
import asyncio
import string
import random
import time

from discord.ext import commands, tasks
from core import models


_LOGGER = logging.getLogger("requiem.plugins.politics_and_war")


v2_url = "https://api.politicsandwar.com/graphql"


class Backend(commands.Cog):
    """
    Caching and event scripts for Politics and War.
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.key = bot.config.pnw_api_key
        self.create_task = bot.loop.create_task

        if not self.key:
            _LOGGER.warning("requiem could not start pnw backend tasks because a key has not been provided!")
            return

        self.handle_nations.error(self.on_task_error)
        self.handle_nations.start()

    def cog_unload(self) -> None:
        """
        Stops all tasks on unload.
        """
        self.handle_nations.stop()

    async def on_task_error(self, *args, **kwargs) -> None:
        """
        Handles catching TypeErrors raised while fetching API queries.
        """
        exc = args[1]

        if isinstance(exc, TypeError):
            _LOGGER.warning("requiem received an error from the API!")
            return

        await self.bot.report_error(exc, "executing a task in politics_and_war.Backend")

    @tasks.loop(minutes=5)
    async def handle_nations(self) -> None:
        """
        Handles fetching of nations. When completed, starts process_nations.
        """
        nations = []
        page = 1

        while True:
            query = """
                {
                  nations(first: 500, page:#) {
                    data {
                      id
                      alliance_id
                      alliance_position
                      nation_name
                      color
                      num_cities
                      vmode
                      beigeturns
                      date
                    }
                  }
                }
                """.replace("#", str(page))
            payload = {"api_key": self.key, "query": query}

            async with aiohttp.ClientSession() as session:
                async with session.get(v2_url, json=payload) as response:
                    returned_json = await response.json(content_type="application/json")

            fetched_nations = returned_json["data"]["nations"]["data"]

            if not fetched_nations:
                break

            nations.extend(fetched_nations)

            page += 1

        await self.process_nations(nations)

    async def process_nations(self, nations: list) -> None:
        """
        Handles stowing and processing of nation events.
        """
        for nation in nations:
            defaults = {
                "nation_name": nation["nation_name"],
                "alliance_id": nation["alliance_id"],
                "alliance_position": nation["alliance_position"],
                "color": nation["color"],
                "cities": nation["num_cities"],
                "vmode_turns": nation["vmode"],
                "beige_turns": nation["beigeturns"],
                "original_creation_date": nation["date"],
                "latest_creation_date": nation["date"]
            }
            entry, created = await models.NationIndex.get_or_create(defaults=defaults, nation_id=nation["id"])

            if created:
                continue

            if int(nation["alliance_id"]) != entry.alliance_id:
                if nation["alliance_position"] == "APPLICANT":
                    self.create_task(self.report_applicant(nation, entry))
                entry.alliance_id = nation["alliance_id"]

            if nation["alliance_position"] != entry.alliance_position:
                entry.alliance_position = nation["alliance_position"]

            if nation["date"] != entry.latest_creation_date:
                self.create_task(self.report_reroll(nation, entry))
                entry.latest_creation_date = nation["date"]

            if int(nation["vmode"]) > entry.vmode_turns == 0:
                self.create_task(self.report_enter_vmode(nation, entry))
                entry.vmode_turns = nation["vmode"]

            elif entry.vmode_turns > int(nation["vmode"]) == 0:
                self.create_task(self.report_exit_vmode(nation, entry))
                entry.vmode_turns = nation["vmode"]

            if int(nation["beigeturns"]) > entry.beige_turns == 0:
                self.create_task(self.report_enter_beige(nation, entry))
                entry.beige_turns = nation["beigeturns"]

            elif entry.beige_turns > int(nation["beigeturns"]) == 0:
                self.create_task(self.report_exit_beige(nation, entry))
                entry.beige_turns = nation["beigeturns"]

            await entry.save()

    async def report_applicant(self, nation, entry) -> None:
        shut_up_pylint = self.bot
        print(f"NATION APPLIED TO JOIN ALLIANCE {nation}")
        await asyncio.sleep(15)

    async def report_reroll(self, nation, entry) -> None:
        shut_up_pylint = self.bot
        print(f"NATION REROLLED {nation}")
        await asyncio.sleep(15)

    async def report_enter_vmode(self, nation, entry) -> None:
        shut_up_pylint = self.bot
        print(f"NATION ENTERED VMODE {nation}")
        await asyncio.sleep(15)

    async def report_exit_vmode(self, nation, entry) -> None:
        shut_up_pylint = self.bot
        print(f"NATION EXITED VMODE {nation}")
        await asyncio.sleep(15)

    async def report_enter_beige(self, nation, entry) -> None:
        shut_up_pylint = self.bot
        print(f"NATION ENTERED BEIGE {nation}")
        await asyncio.sleep(15)

    async def report_exit_beige(self, nation, entry) -> None:
        shut_up_pylint = self.bot
        print(f"NATION EXITED BEIGE {nation}")
        await asyncio.sleep(15)


class PoliticsAndWar(commands.Cog):
    """
    Various informational and utility commands for Politics and War.
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.key = bot.config.pnw_api_key

    async def cog_check(self, ctx) -> bool:
        """
        Returns true if an api key has been configured.
        """
        return bool(self.key)


def setup(bot):
    bot.add_cog(Backend(bot))
    bot.add_cog(PoliticsAndWar(bot))
