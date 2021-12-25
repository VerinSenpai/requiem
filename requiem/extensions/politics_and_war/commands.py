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


from extensions.politics_and_war import helpers
from lightbulb.utils import nav
from lib.utils import human_readable_date

import lightbulb
import pwpy
import hikari


@lightbulb.option("starting", "The starting infrastructure amount.", float)
@lightbulb.option("ending", "The ending infrastructure amount.", float)
@lightbulb.option("cities", "The number of cities to multiply the cost by.", int, default=1)
@lightbulb.command("infracost", "Calculate the cost to purchase or sell infrastructure.")
@lightbulb.implements(lightbulb.SlashCommand)
async def infra_cost(ctx: lightbulb.Context) -> None:
    starting = ctx.options.starting
    ending = ctx.options.ending
    cities = ctx.options.cities

    if cities < 0:
        cities = 1

    cost = pwpy.utils.infra_cost(starting, ending)
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
async def land_cost(ctx: lightbulb.Context) -> None:
    starting = ctx.options.starting
    ending = ctx.options.ending
    cities = ctx.options.cities

    if cities < 0:
        cities = 1

    cost = pwpy.utils.land_cost(starting, ending)
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
async def city_cost(ctx: lightbulb.Context) -> None:
    city = ctx.options.city

    if city >= 2:
        prev_city = city - 1
        cost = pwpy.utils.city_cost(city)

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


@lightbulb.option("nation", "The nation to be viewed. Can be a nation name, leader, or id.")
@lightbulb.command("nationinfo", "View information about a specified nation.")
@lightbulb.implements(lightbulb.SlashCommand)
async def nation_info(ctx: lightbulb.Context) -> None:
    nation = ctx.options.nation
    fetched = await helpers.lookup_nation(nation.lower())
    embed = hikari.Embed()

    if fetched:
        query = """
        nations(first: 1, id: {0}) {{
            data {{
                id
                alliance_id
                alliance_position
                alliance {{
                    name
                    score
                }}
                nation_name
                leader_name
                score
                warpolicy
                dompolicy
                color
                num_cities
                flag
                espionage_available
                last_active
                date
                soldiers
                tanks
                aircraft
                ships
                missiles
                nukes
                offensive_wars {{
                    id
                }}
                defensive_wars {{
                    id
                }}
            }}
        }}
        """.format(fetched)
        key = ctx.bot.credentials.pnw_api_key
        data = await pwpy.api.fetch_query(key, query)
        nations_data = data["nations"]["data"]

        if nations_data:
            nation = nations_data[0]

            nation_name = f"[{nation['nation_name']}]({helpers.NATION_URL}{nation['id']})"
            leader_url = helpers.MESSAGE_URL + nation["leader_name"].replace(" ", "%20")
            leader_name = f"[{nation['leader_name']}]({leader_url})"
            embed.description = f"{nation_name} - {leader_name}"

            embed.add_field(name="Score", value=f"{nation['score']:,}", inline=True)
            embed.add_field(name="Color", value=nation["color"].title(), inline=True)
            cities = nation["num_cities"]
            embed.add_field(name="Cities", value=cities, inline=True)

            creation_date = human_readable_date(nation["date"], '%Y-%m-%d %H:%M:%S')
            embed.add_field(name="Creation Date", value=creation_date)

            if nation["alliance"]:
                alliance_name = f"[{nation['alliance']['name']}]({helpers.ALLIANCE_URL}{nation['alliance_id']})"
                embed.add_field(name="Alliance", value=alliance_name, inline=True)
                embed.add_field(name="Alliance Score", value=f"{nation['alliance']['score']:,}", inline=True)
                embed.add_field(name="Alliance Position", value=nation["alliance_position"].title(), inline=True)

            embed.add_field(name="War Policy", value=nation["warpolicy"], inline=True)
            embed.add_field(name="Domestic Policy", value=nation["dompolicy"], inline=True)

            if nation["espionage_available"]:
                embed.add_field(name="Espionage Available", value="This nation can be spied on!")

            embed.add_field(name="Soldiers", value=f"{nation['soldiers']:,}/{15000 * cities:,}", inline=True)
            embed.add_field(name="Tanks", value=f"{nation['tanks']:,}/{1250 * cities:,}", inline=True)
            embed.add_field(name="Aircraft", value=f"{nation['aircraft']:,}/{75 * cities:,}", inline=True)
            embed.add_field(name="Ships", value=f"{nation['ships']:,}/{15 * cities:,}", inline=True)
            embed.add_field(name="Missiles", value=f"{nation['missiles']:,}", inline=True)
            embed.add_field(name="Nukes", value=f"{nation['nukes']:,}", inline=True)
            embed.set_thumbnail(nation["flag"])

        else:
            embed.description = "The nation specified appears to have been deleted!"

    else:
        embed.description = "No such nation could be found! Please check your query and try again!"

    await ctx.respond(embed=embed)


def process_alliance_selection(key: str, alliance: str or int, embed: hikari.Embed) -> None:
    fetched = await helpers.lookup_alliance(alliance.lower())

    if fetched:
        query = """
        alliances(first: 1, id: {0}) {{
            data {{
                color
                flag
                id
                acronym
                irclink
                name
                score
                nations {{
                    num_cities
                    soldiers
                    tanks
                    aircraft
                    ships
                    missiles
                    nukes
                }}
            }}
        }}
        """.format(fetched)
        data = await pwpy.api.fetch_query(key, query)
        alliances_data = data["alliances"]["data"]

        if alliances_data:
            alliance = alliances_data[0]

            acr = f" ({alliance['acronym']})" if alliance["acronym"] else ""
            header = f"[{alliance['name']}{acr}]({helpers.ALLIANCE_URL}{alliance['id']})"

            if alliance["irclink"]:
                header += f" - [Discord]({alliance['irclink']})"

            embed.description = header

            embed.add_field(name="Score", value=f"{alliance['score']:,}", inline=True)
            embed.add_field(name="Color", value=alliance["color"].title(), inline=True)
            embed.add_field(name="Members", value=str(len(alliance["nations"])), inline=True)

            cities = 0
            soldiers = 0
            tanks = 0
            aircraft = 0
            ships = 0
            missiles = 0
            nukes = 0

            for nation in alliance["nations"]:
                cities += nation["num_cities"]
                soldiers += nation["soldiers"]
                tanks += nation["tanks"]
                aircraft += nation["aircraft"]
                ships += nation["ships"]
                missiles += nation["missiles"]
                nukes += nation["nukes"]

            embed.add_field(name="Soldiers", value=f"{soldiers:,}/{15000 * cities:,}", inline=True)
            embed.add_field(name="Tanks", value=f"{tanks:,}/{1250 * cities:,}", inline=True)
            embed.add_field(name="Aircraft", value=f"{aircraft:,}/{75 * cities:,}", inline=True)
            embed.add_field(name="Ships", value=f"{ships:,}/{15 * cities:,}", inline=True)
            embed.add_field(name="Missiles", value=f"{missiles:,}", inline=True)
            embed.add_field(name="Nukes", value=f"{nukes:,}", inline=True)
            embed.set_thumbnail(alliance["flag"])

        else:
            embed.description = "The alliance specified appears to have been deleted!"

    else:
        embed.description = "No such alliance could be found! Please check your query and try again!"


@lightbulb.option("alliance", "The alliance to be viewed. Can be an alliance name, acronym, or id.")
@lightbulb.option("nation", "Lookup an alliance by a nation. Can be a nation name, leader, or id.")
@lightbulb.command("allianceinfo", "View information about a specified alliance.")
@lightbulb.implements(lightbulb.SlashCommand)
async def alliance_info(ctx: lightbulb.Context) -> None:
    alliance = ctx.options.alliance
    nation = ctx.options.nation
    key = ctx.bot.credentials.pnw_api_key

    embed = hikari.Embed()

    if alliance and nation:
        embed.description = "You can only specify an alliance or a nation, not both!"

    elif nation:
        fetched = await helpers.lookup_nation(nation.lower())

        if fetched:
            query = """
            nations(first: 1, id: {0}) {{
                data {{
                    alliance_id
                }}
            }}
            """.format(fetched)
            data = await pwpy.api.fetch_query(key, query)
            nation_data = data["nations"]["data"][0]

            if nation_data:
                process_alliance_selection(key, nation["alliance_id"], embed)

            else:
                embed.description = "The nation specified appears to have been deleted!"

        else:
            embed.description = "No such nation could be found! Please check your query and try again!"

    else:
        process_alliance_selection(key, alliance, embed)

    await ctx.respond(embed=embed)


async def generate_targets_pages(targets: list) -> list:
    pages = []

    for target in targets:
        nation_name = f"[{target['nation_name']}]({helpers.NATION_URL}{target['id']})"
        leader_url = helpers.MESSAGE_URL + target["leader_name"].replace(" ", "%20")
        leader_name = f"[{target['leader_name']}]({leader_url})"
        page = hikari.Embed(description=f"{nation_name} - {leader_name}")

        page.add_field(name="Score", value=f"{target['score']:,}", inline=True)
        cities = target["num_cities"]
        page.add_field(name="Cities", value=cities, inline=True)
        page.add_field(name="War Policy", value=target["warpolicy"], inline=True)

        if target["alliance"]:
            alliance_name = f"[{target['alliance']['name']}]({helpers.ALLIANCE_URL}{target['alliance_id']})"
            page.add_field(name="Alliance", value=alliance_name, inline=True)
            page.add_field(name="Alliance Score", value=f"{target['alliance']['score']:,}", inline=True)
            page.add_field(name="Alliance Position", value=target["alliance_position"].title(), inline=True)

        if target["espionage_available"]:
            page.add_field(name="Espionage Available", value="This nation can be spied on!")

        page.add_field(name="Soldiers", value=f"{target['soldiers']:,}/{15000 * cities:,}", inline=True)
        page.add_field(name="Tanks", value=f"{target['tanks']:,}/{1250 * cities:,}", inline=True)
        page.add_field(name="Aircraft", value=f"{target['aircraft']:,}/{75 * cities:,}", inline=True)
        page.add_field(name="Ships", value=f"{target['ships']:,}/{15 * cities:,}", inline=True)
        page.add_field(name="Missiles", value=f"{target['missiles']:,}", inline=True)
        page.add_field(name="Nukes", value=f"{target['nukes']:,}", inline=True)

        ongoing_defensive = pwpy.utils.sort_ongoing_wars(target["defensive_wars"])
        page.add_field(name="Ongoing Defensive Wars", value=str(len(ongoing_defensive)), inline=True)
        ongoing_offensive = pwpy.utils.sort_ongoing_wars(target["offensive_wars"])
        page.add_field(name="Ongoing Offensive Wars", value=str(len(ongoing_offensive)), inline=True)

        pages.append(page)

    return pages


@lightbulb.option("score", "The score to use for looking up targets.", float, required=False)
@lightbulb.option("nation", "The nation to use for looking up targets.", required=False)
@lightbulb.option("alliance", "Narrow search to a specific alliance.", int, required=False, default=0)
@lightbulb.option(
    "pirate",
    "Whether or not to include all alliances in search.",
    type=bool,
    required=False,
    default=False
)
@lightbulb.option("powered", "Narrow search to only show powered nations.", bool, required=False, default=True)
@lightbulb.command("raids", "View all raid targets for a given score or nation.")
@lightbulb.implements(lightbulb.SlashCommand)
async def raids(ctx: lightbulb.Context) -> None:
    score = ctx.options.score
    nation = ctx.options.nation
    pirate = ctx.options.pirate
    alliance = None if pirate else ctx.options.alliance
    powered = ctx.options.powered

    targets = None
    key = ctx.bot.credentials.pnw_api_key
    embed = hikari.Embed()

    if score and nation:
        embed.description = "You can only specify either score or nation, not both!"

    elif not nation and not score:
        embed.description = "You must specify a valid score value or a valid nation name/id/leader!"

    elif nation:
        fetched = await helpers.lookup_nation(nation.lower())

        if fetched:
            query = """
            nations(first: 1, id: {0}) {{
                data {{
                    score
                    alliance_id
                }}
            }}
            """.format(fetched)
            data = await pwpy.api.fetch_query(key, query)
            nation_data = data["nations"]["data"][0]

            if nation_data:
                targets = await pwpy.api.within_war_range(
                    key,
                    nation_data["score"],
                    alliance=alliance,
                    powered=powered,
                    omit_alliance=nation_data["alliance_id"]
                )
                if targets:
                    targets = await generate_targets_pages(targets)

                else:
                    embed.description = "No raid targets were found for that nation!"

            else:
                embed.description = "The nation specified appears to have been deleted!"

        else:
            embed.description = "No such nation could be found! Please check your query and try again!"

    else:
        targets = await pwpy.api.within_war_range(
            key,
            score,
            alliance=alliance,
            powered=powered
        )
        if targets:
            targets = await generate_targets_pages(targets)

        else:
            embed.description = "No raid targets were found for that score!"

    if targets:
        navigator = nav.ButtonNavigator(targets)
        await navigator.run(ctx)

    else:
        await ctx.respond(embed=embed)
