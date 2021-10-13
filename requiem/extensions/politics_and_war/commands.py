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


from lightbulb import slash_commands
from pwpy import calc

import hikari


class InfraCost(slash_commands.SlashCommand):

    description = "Calculate the cost to purchase or sell infrastructure."
    starting: int = slash_commands.Option("The starting infrastructure amount.", required=True)
    ending: int = slash_commands.Option("The ending infrastructure amount.", required=True)
    cities: int = slash_commands.Option("The number of cities to multiply the cost by.", required=False, default=1)

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
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
        embed.add_field(name="5% Off", value=f"${cost*.95:,.2f}")
        embed.add_field(name="10% Off", value=f"${cost*.90:,.2f}")
        embed.add_field(name="15% Off", value=f"${cost*.85:,.2f}")
        await ctx.respond(embed=embed)


class LandCost(slash_commands.SlashCommand):

    description = "Calculate the cost to purchase or sell land."
    starting: int = slash_commands.Option("The starting land amount.", required=True)
    ending: int = slash_commands.Option("The ending land amount.", required=True)
    cities: int = slash_commands.Option("The number of cities to multiply the cost by.", required=False, default=1)

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
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
        embed.add_field(name="5% Off", value=f"${cost*.95:,.2f}")
        embed.add_field(name="10% Off", value=f"${cost*.90:,.2f}")
        embed.add_field(name="15% Off", value=f"${cost*.85:,.2f}")
        await ctx.respond(embed=embed)


class CityCost(slash_commands.SlashCommand):

    description = "Calculate the cost to purchase a city."
    city: int = slash_commands.Option("The city to be purchased.")

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
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
            await ctx.send(embed=embed)
