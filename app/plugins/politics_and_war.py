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


import logging
import discord
import typing
import aiohttp
import time


from datetime import datetime, timezone, timedelta
from discord.ext import commands, tasks
from tortoise.query_utils import Q
from utils import paginator
from core import models


_LOGGER = logging.getLogger("requiem.plugins.politics_and_war")
base_url = "https://politicsandwar.com"


async def v3_post(key: str, query: str) -> dict:
    """
    Posts a request to the politics and war graphql api.
    """
    payload = {"api_key": key, "query": query}

    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.politicsandwar.com/graphql", json=payload) as response:
            return await response.json(content_type="application/json")


async def nation_lookup(target: str or int) -> models.Nations:
    """
    Look up a nation using a string. Can be ID, user, name, or leader.
    """
    target = str(target).lower()

    if target.isnumeric():
        q = Q(id=target, snowflake=target, join_type="OR")

    else:
        q = Q(name=target, leader=target, join_type="OR")

    return await models.Nations.get_or_none(q)


async def alliance_lookup(target: str or int) -> models.Alliances:
    """
    Look up an alliance using a string. Can be ID, name, or acronym.
    """
    target = str(target).lower()

    if target.isnumeric():
        q = Q(id=target)

    else:
        q = Q(name=target, acronym=target, join_type="OR")

    return await models.Alliances.get_or_none(q)


class Backend(commands.Cog):
    """
    Caching and event scripts for Politics and War.
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.key = bot.config.pnw_api_key
        self.create_task = bot.loop.create_task

        if not self.key:
            _LOGGER.warning(
                "requiem could not start backend tasks because a key has not been provided!"
            )
            return

        self.fetch_nations.start()
        self.fetch_alliances.start()

    def cog_unload(self) -> None:
        """
        Stops all tasks on unload.
        """
        self.handle_nations.stop()

    @tasks.loop(minutes=5)
    async def fetch_nations(self) -> None:
        """
        Handles fetching of nations. When completed, starts process_nations.
        """
        nations = []
        page = 1

        start = time.time()
        while True:
            query = """
            {
              nations(first:500, page: #) {
                data {
                  id
                  alliance_id
                  alliance_position
                  nation_name
                  leader_name
                  vmode
                  beigeturns
                  last_active
                  date
                }
              }
            }
                """.replace(
                "#", str(page)
            )
            response = await v3_post(self.key, query)
            fetched_nations = response["data"]["nations"]["data"]

            if not fetched_nations:
                break

            nations.extend(fetched_nations)

            page += 1

        await self.process_nations(nations)

    async def process_nations(self, nations: list) -> None:
        """
        Handles stowing and processing of nations.
        """
        for nation in nations:
            defaults = {
                "name": nation["nation_name"].lower(),
                "leader": nation["leader_name"].lower(),
                "alliance": nation["alliance_id"],
                "alliance_position": nation["alliance_position"],
                "vmode_turns": nation["vmode"],
                "beige_turns": nation["beigeturns"],
                "original_creation_date": nation["date"],
                "latest_creation_date": nation["date"],
            }
            entry, created = await models.Nations.get_or_create(
                defaults=defaults, id=nation["id"]
            )

            if created:
                continue

            if nation["nation_name"].lower() != entry.name:
                entry.prev_name = entry.name

            if nation["leader_name"].lower() != entry.leader:
                entry.prev_leader = entry.leader

            if int(nation["alliance_id"]) != entry.alliance:
                if nation["alliance_position"] == "APPLICANT":
                    self.create_task(self.report_applicant(nation, entry))

            if nation["date"] != entry.latest_creation_date:
                self.create_task(self.report_reroll(nation, entry))

            if int(nation["vmode"]) > entry.vmode_turns == 0:
                self.create_task(self.report_enter_vmode(nation, entry))

            if entry.vmode_turns > int(nation["vmode"]) == 0:
                self.create_task(self.report_exit_vmode(nation, entry))

            if int(nation["beigeturns"]) > entry.beige_turns == 0:
                self.create_task(self.report_enter_beige(nation, entry))

            if entry.beige_turns > int(nation["beigeturns"]) == 0:
                self.create_task(self.report_exit_beige(nation, entry))

            entry.name = nation["nation_name"].lower()
            entry.leader = nation["leader_name"].lower()
            entry.alliance = nation["alliance_id"]
            entry.alliance_position = nation["alliance_position"]
            entry.vmode_turns = nation["vmode"]
            entry.beige_turns = nation["beigeturns"]
            entry.latest_creation_date = nation["date"]

            await entry.save()        

    @tasks.loop(minutes=10)
    async def fetch_alliances(self) -> None:
        """
        Handles fetching of alliances.
        """
        alliances = []
        page = 1

        while True:
            query = """
            {
              alliances(first: 50, page: #) {
                data {
                  id
                  name
                  acronym
                  score
                  color
                  flag
                  forumlink
                  irclink
                }
              }
            }
            """.replace(
                "#", str(page)
            )
            response = await v3_post(self.key, query)
            fetched_alliances = response["data"]["alliances"]["data"]

            if not fetched_alliances:
                break

            alliances.extend(fetched_alliances)

            page += 1

        await self.process_alliances(alliances)

    async def process_alliances(self, alliances: list) -> None:
        """
        Handles stowing and processing of nation events.
        """
        for alliance in alliances:
            defaults = {
                "name": alliance["name"].lower(),
                "acronym": alliance["acronym"].lower(),
                "score": alliance["score"],
                "color": alliance["color"],
                "flag": alliance["flag"],
                "forum": alliance["forumlink"],
                "irc": alliance["irclink"]
            }
            entry, created = await models.Alliances.get_or_create(
                defaults=defaults, id=alliance["id"]
            )

            if created:
                continue

            if alliance["name"].lower() != entry.name:
                entry.prev_name = entry.name

            if alliance["acronym"].lower() != entry.acronym:
                entry.prev_acr = entry.acronym

            entry.name = alliance["name"].lower()
            entry.acronym = alliance["acronym"].lower()
            entry.score = alliance["score"]
            entry.color = alliance["color"]
            entry.flag = alliance["flag"]
            entry.forum = alliance["forumlink"]
            entry.irc = alliance["irclink"]

            await entry.save()

    async def report_applicant(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION APPLIED TO JOIN ALLIANCE {nation}")

    async def report_reroll(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION REROLLED {nation}")

    async def report_enter_vmode(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION ENTERED VMODE {nation}")

    async def report_exit_vmode(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION EXITED VMODE {nation}")

    async def report_enter_beige(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION ENTERED BEIGE {nation}")

    async def report_exit_beige(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION EXITED BEIGE {nation}")


class PoliticsAndWar(commands.Cog, name="politics and war"):
    """
    Various informational and utility commands for Politics and War.
    """

    async def cog_check(self, ctx: commands.Context) -> True or None:
        """
        Returns true if an api key has been configured.
        """
        if ctx.bot.config.pnw_api_key and ctx.bot.uptime[0] > 5:
            return True

def setup(bot):
    bot.add_cog(Backend(bot))
    bot.add_cog(PoliticsAndWar())
