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


import aiohttp
import asyncio

from discord.ext import tasks
from datetime import datetime
from core import models
from . import utils


class Scripts:

    def __init__(self, bot):
        self.bot = bot
        self.key = bot.config.pnw_api_key
        self.handle_nations.start()

    @tasks.loop(minutes=10)
    async def handle_nations(self) -> None:
        """
        Fetches nations for event dispatching and indexing.
        """
        update_start = datetime.now()
        futures = []
        page = 0

        async with aiohttp.ClientSession() as session:
            while True:
                page += 1

                query = """
                {
                    nations(first:500, page: #) {
                        data {
                            id
                            nation_name
                            leader_name
                            alliance_id
                            alliance_position
                            score
                            num_cities
                            warpolicy
                            vmode
                            beigeturns
                            color
                            date       
                            soldiers
                            tanks
                            ships
                            aircraft
                            missiles
                            nukes
                        }
                    }
                }
                """.replace("#", str(page))

                response = await utils.v3_post(session, self.key, query)
                nations = response["data"]["nations"]["data"]

                if not nations:
                    break

                for nation in nations:
                    future = asyncio.ensure_future(self.process_nation(nation))
                    futures.append(future)

        await asyncio.gather(*futures)

        all_deleted = await models.Nations.filter(is_deleted=False, last_seen__lt=update_start)
        for entry in all_deleted:
            asyncio.create_task(self.nation_deleted(entry))
            entry.deleted = True
            await entry.save()

    async def process_nation(self, nation: dict) -> None:
        """
        Handles updating of nations table and dispatching of nations events.
        """
        entry, created = await models.Nations.get_or_create(defaults=nation, nation_id=nation["id"])

        if entry.is_deleted:
            asyncio.create_task(self.nation_rerolled(nation, entry))
            entry.is_deleted = False
            entry.is_reroll = True

        if int(nation["alliance_id"]):
            if int(nation["alliance_id"]) != entry.alliance_id:
                if nation["alliance_position"] == "APPLICANT":
                    asyncio.create_task(self.nation_applied_alliance(nation))

                else:
                    asyncio.create_task(self.nation_joined_alliance(nation))
                    await models.AllianceHistory.create(nation_id=entry.nation_id, alliance_id=entry.alliance_id)

            elif nation["alliance_position"] != "APPLICANT" == entry.alliance_position:
                asyncio.create_task(self.nation_joined_alliance(nation))
                await models.AllianceHistory.create(nation_id=entry.nation_id, alliance_id=entry.alliance_id)

            elif created:
                await models.AllianceHistory.create(nation_id=entry.nation_id, alliance_id=entry.alliance_id)

        if nation["nation_name"] != entry.nation_name:
            entry.prev_nation_name = entry.nation_name

        if nation["leader_name"] != entry.leader_name:
            entry.prev_leader_name = entry.prev_leader_name

        if "beige" != nation["color"] != entry.color:
            asyncio.create_task(self.nation_changed_color(nation))

        if nation["vmode"] > entry.vmode == 0:
            asyncio.create_task(self.nation_entered_vmode(nation))

        if 0 == nation["vmode"] < entry.vmode:
            asyncio.create_task(self.nation_exited_vmode(nation))

        if nation["beigeturns"] > entry.beigeturns == 0:
            asyncio.create_task(self.nation_entered_beige(nation))

        if 0 == nation["beigeturns"] < entry.beigeturns:
            asyncio.create_task(self.nation_exited_beige(nation))

        if nation["missiles"] > entry.missiles:
            asyncio.create_task(self.nation_built_missiles(nation))

        if nation["nukes"] > entry.nukes:
            asyncio.create_task(self.nation_built_nukes(nation))

        entry.alliance_id = nation["alliance_id"]
        entry.alliance_position = nation["alliance_position"]
        entry.nation_name = nation["nation_name"]
        entry.leader_name = nation["leader_name"]
        entry.color = nation["color"]
        entry.vmode = nation["vmode"]
        entry.beigeturns = nation["beigeturns"]
        entry.missiles = nation["missiles"]
        entry.nukes = nation["nukes"]

        await entry.save()

    async def nation_applied_alliance(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation applied to join alliance {nation['nation_name']}")

    async def nation_joined_alliance(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation joined alliance {nation['nation_name']}")

    async def nation_changed_color(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation changed color {nation['nation_name']}")

    async def nation_entered_vmode(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation entered vmode {nation['nation_name']}")

    async def nation_exited_vmode(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation exited vmode {nation['nation_name']}")

    async def nation_entered_beige(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation entered beige {nation['nation_name']}")

    async def nation_exited_beige(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation exited beige {nation['nation_name']}")

    async def nation_built_missiles(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation built missile {nation['nation_name']}")

    async def nation_built_nukes(self, nation: dict) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation built nuke {nation['nation_name']}")

    async def nation_rerolled(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation rerolled {nation['nation_name']}")

    async def nation_deleted(self, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation deleted {entry.nation_name}")
