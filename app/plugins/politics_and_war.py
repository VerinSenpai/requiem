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

        self.handle_nations.start()
        self.handle_alliances.start()

    def cog_unload(self) -> None:
        """
        Stops all tasks on unload.
        """
        self.handle_nations.stop()

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
              nations(first:500, page: #) {
                data {
                  id
                  alliance_id
                  alliance_position
                  nation_name
                  leader_name
                  warpolicy
                  dompolicy
                  color
                  num_cities
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
        Handles stowing and processing of nation events.
        """
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
                "original_creation_date": nation["date"],
                "latest_creation_date": nation["date"],
                "soldiers": nation["soldiers"],
                "tanks": nation["tanks"],
                "aircraft": nation["aircraft"],
                "ships": nation["ships"],
                "missiles": nation["missiles"],
                "nukes": nation["nukes"],
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
            entry.latest_creation_date = nation["date"]
            entry.vmode_turns = nation["vmode"]
            entry.beige_turns = nation["beigeturns"]
            entry.cities = nation["num_cities"]
            entry.color = nation["color"]
            entry.color = nation["color"]

            await entry.save()

    @tasks.loop(minutes=5)
    async def handle_alliances(self) -> None:
        """

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

    @commands.command(aliases=["pwla"], brief="List all currently active alliances.")
    @commands.cooldown(1, 2.5)
    async def pwlistaa(self, ctx: commands.Context) -> None:
        """
        List all currently active alliances.
        """
        entries = await models.Alliances.all()
        active = [aa for aa in entries if (datetime.now(timezone.utc) - aa.last_updated).days == 0]

        pages = []
        rank = 1
        embed = discord.Embed(colour=discord.Colour.purple())

        for alliance in sorted(active, key=lambda aa: aa.score, reverse=True):
            embed.add_field(
                name=f"{rank} of {len(active)}",
                value=f"[{alliance.name.title()} ({alliance.acronym})]({base_url}/alliance/id={alliance.id})",
                inline=False
            )
            rank += 1

            if len(embed.fields) == 10:
                pages.append(embed)
                embed = discord.Embed(colour=discord.Colour.purple())

        if embed not in pages:
            pages.append(embed)

        await paginator.Paginator(pages).start(ctx)

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
            since_update = datetime.now(timezone.utc) - entry.last_updated

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

            embed = discord.Embed(
                description=f"{name_url} - {leader_url}", colour=discord.Colour.purple()
            )

            if since_update.days > 0:
                embed.add_field(
                    name="Deleted Nation",
                    value="You are viewing a nation that no longer exists.",
                    inline=False,
                )

            if entry.original_creation_date != entry.latest_creation_date:
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

            if alliance := await alliance_lookup(entry.alliance):  # this probably angers some of you. that's okay.
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
            embed.set_footer(text=f"Nation Last Updated {entry.last_updated}")

        else:
            embed = discord.Embed(
                description="That nation does not exist.",
                colour=discord.Colour.purple(),
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Backend(bot))
    bot.add_cog(PoliticsAndWar())
