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
import aiohttp
import asyncio

from datetime import datetime
from discord.ext import tasks
from . import utils, errors
from core import models


_LOGGER = logging.getLogger("requiem.plugins.politics_and_war.backend")


class Backend:
    """
    Caching and event scripts for Politics and War.
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.key = bot.config.pnw_api_key

        if not self.key:
            _LOGGER.warning(
                "requiem could not start backend tasks because a key has not been provided!"
            )
            return

        self.run_nations.start()

    def cog_unload(self) -> None:
        """
        Stops all tasks on unload.
        """
        self.run_nations.stop()

    @tasks.loop(minutes=10)
    async def run_nations(self) -> None:
        """
        Handles fetching of nations. Starts process_nations.
        """
        try:  # this function needs broken up. it'll happen when it happens.
            last_updated = datetime.now()
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
                                warpolicy
                                dompolicy
                                color
                                score
                                vmode
                                beigeturns
                                last_active
                                date
                                soldiers
                                tanks
                                aircraft
                                ships
                                missiles
                                nukes
                                num_cities
                                cities {
                                    id
                                    name
                                    date
                                    powered
                                    land
                                    infrastructure
                                    airforcebase
                                    aluminumrefinery
                                    bank
                                    barracks
                                    bauxitemine
                                    coalmine
                                    coalpower
                                    drydock
                                    factory
                                    farm
                                    gasrefinery
                                    hospital
                                    ironmine
                                    leadmine
                                    mall
                                    munitionsfactory
                                    nuclearpower
                                    oilpower
                                    oilwell
                                    policestation
                                    recyclingcenter
                                    stadium
                                    steelmill
                                    subway
                                    supermarket
                                    uramine
                                    windpower
                                }
                            }
                            paginatorInfo {
                                hasMorePages
                            }
                        }
                    }
                    """.replace("#", str(page))  # *swallows bleach*

                    response = await utils.v3_post(session, self.key, query)
                    nations = response["data"]["nations"]["data"]

                    if not nations:
                        break

                    for nation in nations:
                        defaults = {
                            "name": nation["nation_name"].lower(),
                            "leader": nation["leader_name"].lower(),
                            "alliance": nation["alliance_id"],
                            "alliance_position": nation["alliance_position"],
                            "war_policy": nation["warpolicy"],
                            "dom_policy": nation["dompolicy"],
                            "color": nation["color"],
                            "cities": nation["num_cities"],
                            "score": nation["score"],
                            "vmode_turns": nation["vmode"],
                            "beige_turns": nation["beigeturns"],
                            "creation_date": nation["date"],
                            "soldiers": nation["soldiers"],
                            "tanks": nation["tanks"],
                            "aircraft": nation["aircraft"],
                            "ships": nation["ships"],
                            "missiles": nation["missiles"],
                            "nukes": nation["nukes"],
                            "last_updated": last_updated
                        }
                        n_entry, _ = await models.Nations.get_or_create(defaults=defaults, id=nation["id"])

                        if n_entry.deleted:
                            asyncio.create_task(self.report_reroll(nation, n_entry))
                            n_entry.deleted = False
                            n_entry.reroll = True
                            n_entry.creation_date = nation["date"]

                        if nation["nation_name"].lower() != n_entry.name:
                            n_entry.prev_name = n_entry.name

                        if nation["leader_name"].lower() != n_entry.leader:
                            n_entry.prev_leader = n_entry.leader

                        if int(nation["alliance_id"]) != n_entry.alliance:
                            if nation["alliance_position"] == "APPLICANT":
                                asyncio.create_task(self.report_applicant(nation, n_entry))

                        if int(nation["vmode"]) > n_entry.vmode_turns == 0:
                            asyncio.create_task(self.report_enter_vmode(nation, n_entry))

                        if n_entry.vmode_turns > int(nation["vmode"]) == 0:
                            asyncio.create_task(self.report_exit_vmode(nation, n_entry))

                        if int(nation["beigeturns"]) > n_entry.beige_turns == 0:
                            asyncio.create_task(self.report_enter_beige(nation, n_entry))

                        if n_entry.beige_turns > int(nation["beigeturns"]) == 0:
                            asyncio.create_task(self.report_exit_beige(nation, n_entry))

                        n_entry.name = nation["nation_name"].lower()
                        n_entry.leader = nation["leader_name"].lower()
                        n_entry.alliance = nation["alliance_id"]
                        n_entry.alliance_position = nation["alliance_position"]
                        n_entry.vmode_turns = nation["vmode"]
                        n_entry.beige_turns = nation["beigeturns"]
                        n_entry.cities = len(nation["cities"])
                        n_entry.color = nation["color"]
                        n_entry.color = nation["color"]
                        n_entry.last_updated = last_updated

                        asyncio.create_task(n_entry.save())

            deleted_nations = await models.Nations.filter(last_updated__not=last_updated, deleted=False)
            for n_entry in deleted_nations:
                n_entry.deleted = True
                await n_entry.save()

        except errors.InvalidAPIKey:  # unloads this plugin if the key is invalid so we don't keep bombarding the api
            _LOGGER.warning(
                "requiem was unable to use the provided pnw_api_key! please verify the key and reload the "
                "politics_and_war extension!"
            )
            self.bot.unload_extension("plugins.politics_and_war")

        except Exception as exc:                         # yes I don't like this either but the method provided by tasks
            await self.bot.on_error("run_nations", exc)  # for handling task errors sucks balls too so

    async def report_applicant(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION APPLIED TO JOIN ALLIANCE {nation['nation_name']}")

    async def report_reroll(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION REROLLED {nation['nation_name']}")

    async def report_enter_vmode(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION ENTERED VMODE {nation['nation_name']}")

    async def report_exit_vmode(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION EXITED VMODE {nation['nation_name']}")

    async def report_enter_beige(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION ENTERED BEIGE {nation['nation_name']}")

    async def report_exit_beige(self, nation: dict, entry: models.Nations) -> None:
        channel = self.bot.get_channel(812669787511324692)
        await channel.send(f"NATION EXITED BEIGE {nation['nation_name']}")