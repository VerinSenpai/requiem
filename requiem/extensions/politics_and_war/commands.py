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


import hikari
import lightbulb
import pwpy


def add_discount_fields(cost: float, embed: hikari.Embed) -> None:
    embed.add_field(name="Base", value=f"${cost:,.2f}")

    if cost > 0:
        embed.add_field(name="5% Off", value=f"${cost * .95:,.2f}")
        embed.add_field(name="10% Off", value=f"${cost * .90:,.2f}")
        embed.add_field(name="15% Off", value=f"${cost * .85:,.2f}")


@lightbulb.command("infra", "Calculate the cost of buying or selling infra.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def infra(ctx: lightbulb.Context) -> None:
    pass


@lightbulb.option(
    name="nation",
    description="The nation to calculate infra costs for.",
    type=str,
    required=True,
)
@lightbulb.option(
    name="target",
    description="The target infra amount.",
    type=float,
    required=True,
    min_value=.01
)
@infra.child()
@lightbulb.command("auto", "Automatically calculate the costs for a given nation or city.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def infra_auto(ctx: lightbulb.Context) -> None:
    await ctx.respond("This command is not ready yet!")


@lightbulb.option(
    name="starting",
    description="The starting infra amount.",
    type=float,
    required=True,
    min_value=.01
)
@lightbulb.option(
    name="target",
    description="The target infra amount.",
    type=float,
    required=True,
    min_value=.01
)
@lightbulb.option(
    name="cities",
    description="The number of cities to multiply th cost by.",
    type=int,
    min_value=1
)
@infra.child()
@lightbulb.command("manual", "Calculate the cost of buying or selling infra.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def infra_manual(ctx: lightbulb.Context) -> None:
    starting = ctx.options.starting
    target = ctx.options.target
    cities = ctx.options.cities
    city_str = "cities" if cities > 1 else "city"
    cost = pwpy.utils.infra_cost(starting, target) * cities
    embed = hikari.Embed(
        title="Infra Cost Calculator",
        description=f"The cost to go from {starting:,.2f} to {target:,.2f} for {cities} {city_str} are as follows"
    )
    add_discount_fields(cost, embed)
    await ctx.respond(embed=embed)
