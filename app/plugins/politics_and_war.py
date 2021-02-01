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
import tortoise
import aiohttp
import logging
import discord
import asyncio
import time

from discord.ext import commands, tasks
from core import models


_LOGGER = logging.getLogger("requiem.plugins.politics_and_war")


v2_url = "https://api.politicsandwar.com/graphql"


async def update_alliance_history(nation: dict) -> None:
    await models.AllianceHistory.create(
        nation_id=nation["id"],
        alliance_id=nation["alliance_id"],
        date_recorded=str(datetime.date.today())
    )


async def nation_lookup(target: str or int or discord.User) -> tortoise.queryset.QuerySetSingle or None:
    """
    Looks up a nation in the database using a given target.
    """
    if isinstance(target, discord.User):
        return await models.Nations.get_or_none(snowflake=target.id)

    try:
        return await models.Nations.get_or_none(nation_id=int(target))

    except ValueError:
        by_name = await models.Nations.get_or_none(nation_name=target.lower())
        by_leader = await models.Nations.get_or_none(nation_leader=target.lower())
        return by_name or by_leader


async def post(key: str, query: str) -> dict:
    """
    Posts to the pnw api with a key and query.
    """
    payload = {"api_key": key, "query": query}

    async with aiohttp.ClientSession() as session:
        async with session.get(v2_url, json=payload) as response:
            return await response.json(content_type="application/json")


async def quick_send(ctx: commands.Context, message: str) -> None:
    """
    Creates an embed and sends a given message.
    """
    embed = discord.Embed(
        description=message,
        colour=discord.Colour.purple()
    )
    await ctx.send(embed=embed)


class Backend(commands.Cog):
    """
    Caching and event scripts for Politics and War.
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        self.key = bot.config.pnw_api_key
        self.create_task = bot.loop.create_task

        if not self.key:
            _LOGGER.warning("requiem could not start pnw tasks because a key has not been provided!")
            return

        self.fetch_nations.start()

    def cog_unload(self) -> None:
        """
        Stops all tasks on unload.
        """
        self.fetch_nations.stop()

    @tasks.loop(minutes=5)
    async def fetch_nations(self):
        nations = []
        page = 1

        while True:
            query = """
                {
                  nations(first: 500, vmode: false, page:#) {
                    data {
                      id
                      nation_name
                      leader_name
                      alliance_id
                      alliance_position
                      date
                    }
                    paginatorInfo {
                      hasMorePages
                    }
                  }
                }
                """.replace("#", str(page))
            returned_json = await post(self.key, query)
            data = returned_json.get("data")

            if not data:
                _LOGGER.warning("requiem was unable fetch nations! is your api key correct?")
                return

            nations.extend(data["nations"]["data"])

            #  blame the api team for this ass
            if not data["nations"]["paginatorInfo"]["hasMorePages"]:
                break

            page += 1

        await self.handle_nations(nations)

    async def handle_nations(self, nations: list) -> None:
        """
        Handles stowing of nations in the database and dispatching of nations events.
        """
        for nation in nations:
            defaults = {
                "nation_name": nation["nation_name"].lower(),
                "nation_leader": nation["leader_name"].lower(),
                "alliance_id": nation["alliance_id"],
                "alliance_position": nation["alliance_position"],
                "creation_date": nation["date"]
            }
            saved, created = await models.Nations.get_or_create(defaults, nation_id=nation["id"])
            filtered = models.Nations.filter(nation_id=nation["id"])

            if saved.creation_date != nation["date"]:
                await filtered.update(is_reroll=True)
                self.create_task(self.dispatch_reroll_notification(nation, saved))

            if int(nation["alliance_id"]) != 0 and nation["alliance_position"] != "APPLICANT":
                await models.AllianceHistory.get_or_create(
                    nation_id=nation["id"],
                    alliance_id=nation["alliance_id"]
                )

            if saved.alliance_id != int(nation["alliance_id"]):
                if int(nation["alliance_id"]) != 0 and nation["alliance_position"] == "APPLICANT":
                    self.create_task(self.dispatch_applicant_notification(nation, saved))
                await filtered.update(
                    alliance_id=nation["alliance_id"],
                    alliance_position=nation["alliance_position"]
                )

            elif nation["alliance_position"] != saved.alliance_position:
                await filtered.update(alliance_position=nation["alliance_position"])

    async def dispatch_reroll_notification(self, nation: dict, config: models.Nations) -> None:
        print(f"Event dispatched ~~ {nation}")
        shut_up_pylint = self.bot
        await asyncio.sleep(15)

    async def dispatch_applicant_notification(self, nation: dict, config: models.Nations) -> None:
        print(f"Event dispatched! ~~ {config.alliance_id} ~~ {nation}")
        shut_up_pylint = self.bot
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

    @commands.command(brief="Provides information about a given nation.")
    @commands.cooldown(1, 2.5)
    async def nation(self, ctx: commands.Context, *, target: str = None) -> None:
        """
        Provides information about a given nation.
        """
        if not target:
            target = ctx.author.id

        try:
            target = await commands.UserConverter().convert(ctx, str(target))
        except commands.BadArgument:
            pass

        entry = await nation_lookup(target)
        if not entry:
            return await quick_send(ctx, "That nation was not found!")

        query = """
        {
          nations(first: 1, id: #) {
            data {
              id
              alliance {
                name
              }
              alliance_id
              alliance_position
              nation_name
              leader_name
              warpolicy
              dompolicy
              color
              num_cities
              score
              last_active
              soldiers
              tanks
              aircraft
              ships
              missiles
              nukes
              projects
            }
          }
        }
        """.replace("#", str(entry.nation_id))
        returned_json = await post(self.key, query)

        data = returned_json.get("data")
        if not data:
            return await quick_send(ctx, "There was an issue with the API response!")

        data = data["nations"]["data"]
        if not data:
            return await quick_send(ctx, "That nation no longer exists!")

        nation = data[0]
        leader = nation["leader_name"]
        leader = f"[{leader}](https://politicsandwar.com/inbox/message/receiver={leader.replace(' ', '%20')})"

        embed = discord.Embed(
            description=f"[{nation['nation_name']}](https://politicsandwar.com/nation/id={nation['id']}) - {leader}",
            colour=discord.Colour.purple()
        )
        if nation["alliance"]:
            embed.add_field(name="Alliance", value=f"[{nation['alliance']['name']}](https://politicsandwar.com/alliance"
                                                   f"/id={nation['alliance_id']})")
            embed.add_field(name="Position", value=nation["alliance_position"].title())
        embed.add_field(name="Score", value=nation["score"])
        embed.add_field(name="Color", value=nation["color"].title())
        embed.add_field(name="Cities", value=nation["num_cities"])
        embed.add_field(name="War Policy", value=nation["warpolicy"])
        embed.add_field(name="Domestic Policy", value=nation["dompolicy"])
        embed.add_field(name="Soldiers", value=nation["soldiers"])
        embed.add_field(name="Tanks", value=nation["tanks"])
        embed.add_field(name="Aircraft", value=nation["aircraft"])
        embed.add_field(name="Ships", value=nation["ships"])
        embed.add_field(name="Missiles", value=nation["missiles"])
        embed.add_field(name="Nukes", value=nation["nukes"])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Backend(bot))
    bot.add_cog(PoliticsAndWar(bot))
