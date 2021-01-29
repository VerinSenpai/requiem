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


import tortoise
import aiohttp
import logging
import discord

from discord.ext import commands, tasks
from core import models


_LOGGER = logging.getLogger("requiem.plugins.politics_and_war")


v2_url = "https://api.politicsandwar.com/graphql"


async def nation_lookup(target: str or int or discord.User) -> tortoise.queryset.QuerySetSingle or None:
    """
    Looks up a nation in the database using a given target.
    """
    if isinstance(target, discord.User) or isinstance(target, discord.Member):
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


class PoliticsAndWarStowingScripts(commands.Cog):
    """
    Caching scripts for Politics and War.
    """

    def __init__(self, bot) -> None:
        self.key = bot.config.pnw_api_key

        if not self.key:
            _LOGGER.warning("requiem could not start pnw tasks because a key has not been provided!")
            return

        self.stow_nations.start()

    def cog_unload(self) -> None:
        """
        Stops all tasks on unload.
        """
        self.stow_nations.stop()

    @tasks.loop(minutes=5)
    async def stow_nations(self) -> None:
        """
        Fetches nation id information and stores it in the database.
        """
        page = 1

        while True:
            query = """
                {
                  nations(first: 500, vmode: false, page:#) {
                    data {
                      id
                      alliance_id
                      nation_name
                      leader_name
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
                _LOGGER.warning("requiem was unable fetch nations for stowing! is your api key correct?")
                return

            for nation in data["nations"]["data"]:
                defaults = {
                    "alliance_id": nation["alliance_id"],
                    "nation_name": nation["nation_name"].lower(),
                    "nation_leader": nation["leader_name"].lower()
                }
                await models.Nations.get_or_create(defaults, nation_id=nation["id"])

            if not data["nations"]["paginatorInfo"]["hasMorePages"]:
                break

            page += 1


class PoliticsAndWar(commands.Cog):
    """
    Various informational and utility commands for Politics and War.
    """

    def __init__(self, bot) -> None:
        self.key = bot.config.pnw_api_key

    async def cog_check(self, ctx) -> bool:
        """
        Returns true if an api key has been configured.
        """
        return bool(self.key)

    @commands.command(brief="Provides information about a given nation.")
    @commands.cooldown(1, 2.5)
    async def nation(self, ctx: commands.Context, *, target: str) -> None:
        """
        Provides information about a given nation.
        """
        if not target:
            target = ctx.author

        try:
            target = await commands.UserConverter().convert(ctx, target)
        except commands.BadArgument:
            pass

        entry = await nation_lookup(target)
        if not entry:
            embed = discord.Embed(
                description="That nation was not found! If you believe this to be a mistake, wait a few minutes and "
                            "try again!",
                colour=discord.Colour.purple()
            )
            await ctx.send(embed=embed)
            return

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
            embed = discord.Embed(
                description="The API returned something other than expected! This could be an API key related issue!",
                colour=discord.Colour.purple()
            )
            await ctx.send(embed=embed)
            return

        data = data["nations"]["data"]
        if not data:
            embed = discord.Embed(
                description="That nation no longer exists!",
                colour=discord.Colour.purple()
            )
            await ctx.send(embed=embed)
            return

        nation = data[0]
        leader = f"[{nation['leader_name']}](https://politicsandwar.com/inbox/message/receiver=" \
                 f"{nation['leader_name'].replace(' ', '%20')})"

        embed = discord.Embed(
            description=f"[{nation['nation_name']}](https://politicsandwar.com/nation/id={nation['id']}) - {leader}",
            colour=discord.Colour.purple()
        )
        if nation["alliance"]:
            embed.add_field(name="Alliance", value=f"[{nation['alliance']['name']}](https://politicsandwar.com/alliance"
                                                   f"/id={nation['alliance_id']})")
            embed.add_field(name="Position", value=nation["alliance_position"].title())
        embed.add_field(name="Score", value=nation["score"], inline=False)
        embed.add_field(name="Color", value=nation["color"].title(), inline=False)
        embed.add_field(name="Cities", value=nation["num_cities"], inline=False)
        embed.add_field(name="War Policy", value=nation["warpolicy"], inline=False)
        embed.add_field(name="Domestic Policy", value=nation["dompolicy"], inline=False)
        embed.add_field(name="Soldiers", value=nation["soldiers"])
        embed.add_field(name="Tanks", value=nation["tanks"])
        embed.add_field(name="Aircraft", value=nation["aircraft"])
        embed.add_field(name="Ships", value=nation["ships"])
        embed.add_field(name="Missiles", value=nation["missiles"])
        embed.add_field(name="Nukes", value=nation["nukes"])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PoliticsAndWarStowingScripts(bot))
    bot.add_cog(PoliticsAndWar(bot))
