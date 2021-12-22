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


from extensions.politics_and_war import utils, queries
from pwpy import calc, api
from lightbulb.utils import nav

import lightbulb
import hikari


@lightbulb.option("starting", "The starting infrastructure amount.", float)
@lightbulb.option("ending", "The ending infrastructure amount.", float)
@lightbulb.option("cities", "The number of cities to multiply the cost by.", int, default=1)
@lightbulb.command("infracost", "Calculate the cost to purchase or sell infrastructure.")
@lightbulb.implements(lightbulb.SlashCommand)
async def infracost(ctx: lightbulb.Context) -> None:
    starting = ctx.options.starting
    ending = ctx.options.ending
    cities = ctx.options.cities

    if cities < 0:
        cities = 1

    cost = calc.infra_cost(starting, ending)
    cost *= cities

    city_str = "city" if cities == 1 else "cities"
    output = f"The cost to go from {starting:,.2f} to {ending:,.2f} for {cities} {city_str} are as follows"

    embed = hikari.Embed(description=output)
    embed.add_field(name="Base", value=f"${cost:,.2f}")
    embed.add_field(name="5% Off", value=f"${cost * .95:,.2f}")
    embed.add_field(name="10% Off", value=f"${cost * .90:,.2f}")
    embed.add_field(name="15% Off", value=f"${cost * .85:,.2f}")
    await ctx.respond(embed=embed)


@lightbulb.option("starting", "The starting land amount.", float)
@lightbulb.option("ending", "The ending land amount.", float)
@lightbulb.option("cities", "The number of cities to multiply the cost by.", int, default=1)
@lightbulb.command("landcost", "Calculate the cost to purchase or sell land.")
@lightbulb.implements(lightbulb.SlashCommand)
async def landcost(ctx: lightbulb.Context) -> None:
    starting = ctx.options.starting
    ending = ctx.options.ending
    cities = ctx.options.cities

    if cities < 0:
        cities = 1

    cost = calc.land_cost(starting, ending)
    cost *= cities

    city_str = "city" if cities == 1 else "cities"
    output = f"The cost to go from {starting:,.2f} to {ending:,.2f} for {cities} {city_str} are as follows"

    embed = hikari.Embed(description=output)
    embed.add_field(name="Base", value=f"${cost:,.2f}")
    embed.add_field(name="5% Off", value=f"${cost * .95:,.2f}")
    embed.add_field(name="10% Off", value=f"${cost * .90:,.2f}")
    embed.add_field(name="15% Off", value=f"${cost * .85:,.2f}")
    await ctx.respond(embed=embed)


@lightbulb.option("city", "The city to be purchased.", int, default=2)
@lightbulb.command("citycost", "Calculate the cost to purchase a city.")
@lightbulb.implements(lightbulb.SlashCommand)
async def citycost(ctx: lightbulb.Context) -> None:
    city = ctx.options.city

    if city >= 2:
        prev_city = city - 1
        cost = calc.city_cost(city)

        output = f"The cost to go from city {prev_city} to {city} are as follows"
        embed = hikari.Embed(description=output)
        embed.add_field(name="Base", value=f"${cost:,.2f}")
        embed.add_field(name="5% Off", value=f"${cost * .95:,.2f}")

        if city >= 12:
            embed.add_field(name="UP + 5% Off", value=f"${(cost - 50000000) * .95:,.2f}")

        if city >= 17:
            embed.add_field(name="AUP + 5% Off", value=f"${(cost - 150000000) * .95:,.2f}")

        await ctx.respond(embed=embed)

    else:
        output = "You must specify a city greater than 1 to be purchased!"
        embed = hikari.Embed(description=output)
        await ctx.respond(embed=embed)


@lightbulb.option("target", "The nation to be viewed. Can be a nation name, leader, or id.")
@lightbulb.command("nationinfo", "View information about a specified nation.")
@lightbulb.implements(lightbulb.SlashCommand)
async def nationinfo(ctx: lightbulb.Context) -> None:
    target = ctx.options.target
    fetched = await utils.lookup_nation(target.lower())
    embed = hikari.Embed()

    if fetched:
        query = queries.nation_lookup_query.format(fetched)
        key = ctx.bot.credentials.pnw_api_key
        data = await api.fetch_query(key, query)
        nations_data = data["nations"]["data"]

        if nations_data:
            nation = nations_data[0]
            utils.build_nation_info_fields(nation, embed)

        else:
            embed.description = "The nation specified appears to have been deleted!"

    else:
        embed.description = "No such nation could be found! Please check your query and try again!"

    await ctx.respond(embed=embed)


@lightbulb.option("score", "The score to use for looking up targets.", type=float, required=False)
@lightbulb.option("nation", "The nation to use for looking up targets.", required=False)
@lightbulb.command("raids", "View all raid targets for a given score or nation.")
@lightbulb.implements(lightbulb.SlashCommand)
async def raids(ctx: lightbulb.Context) -> None:
    key = ctx.bot.credentials.pnw_api_key
    score = ctx.options.score
    nation = ctx.options.nation
    embed = hikari.Embed()

    if score and nation:
        embed.description = "You can only specify either score or nation, not both!"

    elif not nation and not score:
        embed.description = "You must specify a valid score value or a valid nation name/id/leader!"

    elif nation:
        fetched = await utils.lookup_nation(nation.lower())

        if fetched:
            query = queries.nation_score_query.format(fetched)
            data = await api.fetch_query(key, query)
            nations_data = data["nations"]["data"]

            if nations_data:
                score = nations_data[0]["score"]

            else:
                embed.description = "The nation specified appears to have been deleted!"

        else:
            embed.description = "No such nation could be found! Please check your query and try again!"

    if score:
        targets = await api.within_war_range(key, score)

        if targets:
            pages = []
            in_page = 0
            page = hikari.Embed()

            for target in targets:
                if in_page > 10:
                    pages.append(page)
                    page = hikari.Embed()
                    in_page = 0

                page.add_field(
                    name=f"{target['nation_name']} {target['leader_name']}",
                    value=target["score"],
                )
                in_page += 1

            if page not in pages:
                pages.append(page)

            navigator = nav.ButtonNavigator(pages)
            await navigator.run(ctx)
            return

        else:
            embed.description = "There were no targets found for that nation/score!"

    await ctx.respond(embed=embed)


