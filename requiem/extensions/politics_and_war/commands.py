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

            embed.add_field(name="Name", value=nation["nation_name"])
            embed.add_field(name="Leader", value=nation["leader_name"])
            embed.add_field(name="Score", value=f"{nation['score']:,}")

            if nation["alliance"]:
                embed.add_field(name="Alliance", value=nation["alliance"]["name"])
                embed.add_field(name="Alliance Score", value=f"{nation['alliance']['score']:,}")
                embed.add_field(name="Alliance Position", value=nation["alliance_position"].title())

            embed.add_field(name="War Policy", value=nation["warpolicy"])
            embed.add_field(name="Domestic Policy", value=nation["dompolicy"])
            embed.add_field(name="Color", value=nation["color"].title())
            embed.add_field(name="Cities", value=nation["num_cities"])
            embed.add_field(name="Espionage Available", value=nation["espionage_available"])
            embed.add_field(name="Soldiers", value=f"{nation['soldiers']:,}")
            embed.add_field(name="Tanks", value=f"{nation['tanks']:,}")
            embed.add_field(name="Aircraft", value=f"{nation['aircraft']:,}")
            embed.add_field(name="Ships", value=f"{nation['ships']:,}")
            embed.add_field(name="Missiles", value=f"{nation['missiles']:,}")
            embed.add_field(name="Nukes", value=f"{nation['nukes']:,}")
            embed.set_thumbnail(nation["flag"])

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
            count = 0

            for target in targets:
                count += 1

                nation_name = f"[{target['nation_name']}]({utils.NATION_URL}{target['id']})"
                leader_name = f"[{target['leader_name']}]({utils.MESSAGE_URL}{target['leader_name']})"
                page = hikari.Embed(description=f"{nation_name} - {leader_name}")

                page.add_field(name="Score", value=target["score"])
                cities = target["num_cities"]
                page.add_field(name="Cities", value=cities)
                page.add_field(name="Soldiers", value=f"{target['soldiers']}/{15000 * cities}")
                page.add_field(name="Tanks", value=f"{target['tanks']}/{1250 * cities}")
                page.add_field(name="Aircraft", value=f"{target['aircraft']}/{75 * cities}")
                page.add_field(name="Ships", value=f"{target['ships']}/{15 * cities}")
                page.add_field(name="Missiles", value=f"{target['missiles']}")
                page.add_field(name="Nukes", value=f"{target['nukes']}")

                if target["espionage_available"]:
                    page.add_field(name="Espionage Available", value="This nation can be spied on!")

                page.set_footer(text=f"Page {count} of {len(targets)}")
                pages.append(page)

            navigator = nav.ButtonNavigator(pages)
            await navigator.run(ctx)
            return

        else:
            embed.description = "There were no targets found for that nation/score!"

    await ctx.respond(embed=embed)


