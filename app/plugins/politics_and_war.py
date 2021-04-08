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
import asyncio
import timeago

from datetime import datetime, timezone, timedelta
from discord.ext import commands, tasks
from tortoise.query_utils import Q
from utils import paginator
from core import models


_LOGGER = logging.getLogger("requiem.plugins.politics_and_war")
base_url = "https://politicsandwar.com"


async def v3_post(session: aiohttp.ClientSession, key: str, query: str) -> dict:
    """
    Posts a request to the pnw graphql api.
    """
    payload = {"api_key": key, "query": query}

    async with session.get("https://api.politicsandwar.com/graphql", json=payload) as response:
        if response.status == 401:
            raise InvalidAPIKey("There was an issue with the provided api key!")
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


class InvalidAPIKey(Exception):
    """
    There was an issue with the provided api key.
    """


class Backend(commands.Cog):
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

                    response = await v3_post(session, self.key, query)
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

                        for city in nation["cities"]:
                            defaults = {
                                "nation": nation["id"],
                                "name": city["name"],
                                "date": city["date"],
                                "powered": city["powered"],
                                "infra": city["infrastructure"],
                                "land": city["land"],
                                "nuclearpower": city["nuclearpower"],
                                "oilpower": city["oilpower"],
                                "coalpower": city["coalpower"],
                                "windpower": city["windpower"],
                                "bauxitemine": city["bauxitemine"],
                                "coalmine": city["coalmine"],
                                "ironmine": city["ironmine"],
                                "leadmine": city["leadmine"],
                                "oilwell": city["oilwell"],
                                "uramine": city["uramine"],
                                "farm": city["farm"],
                                "aluminumrefinery": city["aluminumrefinery"],
                                "munitionsfactory": city["munitionsfactory"],
                                "steelmill": city["steelmill"],
                                "gasrefinery": city["gasrefinery"],
                                "hospital": city["hospital"],
                                "policestation": city["policestation"],
                                "recyclingcenter": city["recyclingcenter"],
                                "subway": city["subway"],
                                "mall": city["mall"],
                                "bank": city["bank"],
                                "supermarket": city["supermarket"],
                                "stadium": city["stadium"],
                                "barracks": city["barracks"],
                                "airforcebase": city["airforcebase"],
                                "drydock": city["drydock"],
                                "factory": city["factory"],
                                "last_updated": last_updated
                            }
                            c_entry, _ = await models.Cities.get_or_create(defaults=defaults, id=city["id"])

                            c_entry.name = city["name"]
                            c_entry.powered = city["powered"]
                            c_entry.infra = city["infrastructure"]
                            c_entry.land = city["land"]
                            c_entry.nuclearpower = city["nuclearpower"]
                            c_entry.oilpower = city["oilpower"]
                            c_entry.coalpower = city["coalpower"]
                            c_entry.windpower = city["windpower"]
                            c_entry.bauxitemine = city["bauxitemine"]
                            c_entry.coalmine = city["coalmine"]
                            c_entry.ironmine = city["ironmine"]
                            c_entry.leadmine = city["leadmine"]
                            c_entry.oilwell = city["oilwell"]
                            c_entry.uramine = city["uramine"]
                            c_entry.farm = city["farm"]
                            c_entry.aluminumrefinery = city["aluminumrefinery"]
                            c_entry.munitionsrefinery = city["munitionsfactory"]
                            c_entry.steelmill = city["steelmill"]
                            c_entry.gasrefinery = city["gasrefinery"]
                            c_entry.hospital = city["hospital"]
                            c_entry.policestation = city["policestation"]
                            c_entry.recyclingcenter = city["recyclingcenter"]
                            c_entry.subway = city["subway"]
                            c_entry.mall = city["mall"]
                            c_entry.bank = city["bank"]
                            c_entry.supermarket = city["supermarket"]
                            c_entry.statium = city["stadium"]
                            c_entry.barracks = city["barracks"]
                            c_entry.airforcebase = city["airforcebase"]
                            c_entry.drydock = city["drydock"]
                            c_entry.factory = city["factory"]
                            c_entry.last_updated = last_updated

                            asyncio.create_task(c_entry.save())

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

            deleted_cities = await models.Cities.filter(last_updated__not=last_updated)
            for c_entry in deleted_cities:
                await c_entry.delete()

        except InvalidAPIKey:  # unloads this plugin if the key is invalid so we don't keep bombarding the api
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


class PoliticsAndWar(commands.Cog, name="politics and war"):
    """
    Various informational and utility commands for Politics and War.
    """

    @commands.group(aliases=["pwna"], brief="View a given nation.")
    @commands.cooldown(1, 2.5)
    async def pwnation(
        self, ctx: commands.Context, *, target: typing.Union[discord.User, str] = None
    ) -> None:
        """
        View information about a nation.

        You can look a nation up by its id, name, or a discord user (if they've linked themselves to their nation)
        If you don't specify a target, a lookup is performed for a nation linked to your discord.
        """
        target = target or ctx.author.id

        if isinstance(target, discord.User):
            target = target.id

        entry = await nation_lookup(target)

        if entry:
            name = (
                f"{entry.name} (formerly {entry.prev_name})"
                if entry.prev_name
                else entry.name
            )
            leader = (
                f"{entry.leader} (formerly {entry.leader})"
                if entry.prev_leader
                else entry.leader
            )

            name_url = f"[{name.title()}]({base_url}/nation/id={entry.id})"
            leader_url = f"[{leader.title()}]({base_url}/inbox/message/receiver={leader.replace(' ', '+')})"
            embed = discord.Embed(description=f"{name_url} - {leader_url}", colour=discord.Colour.purple())

            if entry.deleted:
                embed.add_field(
                    name="Deleted Nation",
                    value="You are viewing a nation that no longer exists.",
                    inline=False,
                )

            if entry.reroll:
                embed.add_field(
                    name="Re-roll",
                    value="You are viewing a nation that has re-rolled.",
                    inline=False,
                )

            if entry.vmode_turns:
                embed.add_field(
                    name="Vacation Mode",
                    value=f"This nation is in vacation mode for {entry.vmode_turns} more turns.",
                    inline=False,
                )

            if entry.beige_turns:
                embed.add_field(
                    name="Beige",
                    value=f"This nation is on beige for {entry.beige_turns} more turns.",
                    inline=False,
                )

            if alliance := await alliance_lookup(entry.alliance):
                embed.add_field(name="Alliance", value=f"{alliance.name.title()} ({alliance.acronym})")
                embed.add_field(name="Position", value=f"{entry.alliance_position.title()}")
                embed.add_field(name="IRC/Discord", value=alliance.irc, inline=False)

            elif entry.alliance:
                embed.add_field(name="Alliance", value="Unknown Alliance", inline=False)

            embed.add_field(name="War Policy", value=entry.war_policy.title())
            embed.add_field(name="Domestic Policy", value=entry.dom_policy.title())
            embed.add_field(name="Color", value=entry.color.title())
            embed.add_field(name="Cities", value=str(entry.cities))
            embed.add_field(name="Score", value=f"{entry.score:,}")
            embed.add_field(name="Soldiers", value=f"{entry.soldiers:,}")
            embed.add_field(name="Tanks", value=f"{entry.tanks:,}")
            embed.add_field(name="Aircraft", value=f"{entry.aircraft:,}")
            embed.add_field(name="Ships", value=f"{entry.ships:,}")
            embed.add_field(name="Missiles", value=f"{entry.missiles:,}")
            embed.add_field(name="Nukes", value=f"{entry.nukes:,}")

            last_updated = timeago.format(entry.last_updated, datetime.now(tz=timezone.utc))
            embed.set_footer(text=f"Nation last updated {last_updated}")

        else:
            embed = discord.Embed(
                description="That nation does not exist.",
                colour=discord.Colour.purple(),
            )

        await ctx.send(embed=embed)
