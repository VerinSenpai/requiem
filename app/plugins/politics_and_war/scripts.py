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
import time
import pytz

from discord.ext import tasks
from datetime import datetime, timezone
from core import models
from . import utils


class Scripts:

    def __init__(self, bot):
        self.bot = bot
        self.key = bot.config.pnw_api_key
        self.gather_nations.start()

    @tasks.loop(minutes=10)
    async def gather_nations(self) -> None:
        """
        Handles fetching of nations. Starts process_nations.
        """
        try:
            page = 0

            async with aiohttp.ClientSession() as session:
                while True:
                    page += 1

                    query = """
                    {
                        nations(first:400, page: #) {
                            data {
                                id
                                alliance_id
                                alliance_position
                                nation_name
                                leader_name
                                color
                                vmode
                                beigeturns
                                date
                            }
                        }
                    }
                    """.replace("#", str(page))

                    response = await utils.v3_post(session, self.key, query)
                    nations = response["data"]["nations"]["data"]

                    if not nations:
                        break

                    for nation in nations:
                        asyncio.create_task(self.process_nation(nation))

        except Exception as exc:
            await self.bot.on_error(exc, "gather_nations")

    async def process_nation(self, nation: dict) -> None:
        try:
            entry, created = await models.Nations.get_or_create(defaults=nation, nation_id=nation["id"])

            if int(nation["alliance_id"]):
                if int(nation["alliance_id"]) != entry.alliance_id:
                    if nation["alliance_position"] == "APPLICANT":
                        asyncio.create_task(self.nation_applied_alliance(nation, entry))

                    else:
                        asyncio.create_task(self.nation_joined_alliance(nation, entry))
                        await models.AllianceHistory.create(nation_id=entry.nation_id, alliance_id=entry.alliance_id)

                elif nation["alliance_position"] != "APPLICANT" == entry.alliance_position:
                    asyncio.create_task(self.nation_joined_alliance(nation, entry))
                    await models.AllianceHistory.create(nation_id=entry.nation_id, alliance_id=entry.alliance_id)

                elif created:
                    await models.AllianceHistory.create(nation_id=entry.nation_id, alliance_id=entry.alliance_id)

            if nation["vmode"] > entry.vmode == 0:
                asyncio.create_task(self.nation_entered_vmode(nation, entry))

            if 0 == nation["vmode"] < entry.vmode:
                asyncio.create_task(self.nation_exited_vmode(nation, entry))

            if nation["beigeturns"] > entry.beigeturns == 0:
                asyncio.create_task(self.nation_entered_beige(nation, entry))

            if 0 == nation["beigeturns"] < entry.beigeturns:
                asyncio.create_task(self.nation_exited_beige(nation, entry))

            creation_date = datetime.strptime(nation["date"], "%Y-%m-%d %H:%M:%S")
            if creation_date != entry.date.replace(tzinfo=None):
                asyncio.create_task(self.nation_rerolled(nation, entry))

            entry.alliance_id = nation["alliance_id"]
            entry.alliance_position = nation["alliance_position"]
            entry.nation_name = nation["nation_name"]
            entry.leader_name = nation["leader_name"]
            entry.color = nation["color"]
            entry.vmode = nation["vmode"]
            entry.beigeturns = nation["beigeturns"]
            entry.latest_date = creation_date

            await entry.save()

        except Exception as exc:
            await self.bot.report_error(exc, "process_nation")

    async def nation_applied_alliance(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation applied to join alliance {nation['nation_name']}")

    async def nation_joined_alliance(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation joined alliance {nation['nation_name']}")

    async def nation_entered_vmode(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation entered vmode {nation['nation_name']}")

    async def nation_exited_vmode(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation exited vmode {nation['nation_name']}")

    async def nation_entered_beige(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation entered beige {nation['nation_name']}")

    async def nation_exited_beige(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation exited beige {nation['nation_name']}")

    async def nation_rerolled(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"nation rerolled {nation['nation_name']}")
