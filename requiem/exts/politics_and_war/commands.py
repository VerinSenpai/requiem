# This is part of Requiem
# Copyright (C) 2020  Verin Senpai
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from calendar import leapdays

from requiem.core.impl import RequiemContext, RequiemPlugin
from requiem.core.models import AutoCompleteIndex, NationStore
from requiem.exts.politics_and_war import queries
from lightbulb.ext import tasks

import pwpy
import lightbulb
import hikari
import logging


_LOGGER = logging.getLogger("pw.commands")


plugin = RequiemPlugin("pw")


@tasks.task(s=1, max_executions=1)
async def setup():
    api_key: str | None = plugin.config.pw.api_key

    if api_key:
        pwpy.set_global_key(api_key)

        try:
            await pwpy.get_query(queries.GAME_DATE)
            update_indexes.start()

        except pwpy.QueryKeyError:
            _LOGGER.warning("provided api_key is invalid! pw commands and features will be unavailable!")

    else:
        _LOGGER.warning("api_key not provided! pw commands and features will be unavailable!")


NATIONS = AutoCompleteIndex()


@tasks.task(m=10)
async def update_nations_index():
    ...


@tasks.task(m=10)
async def update_alliances_index():
    ...


@tasks.task(m=10)
async def update_indexes():
    global NATIONS

    response = await pwpy.get_query(queries.NATIONS_PAGES, parser=pwpy.PaginatorInfo)

    bulk_query = pwpy.BulkQuery()
    for page in range(1, response.nations.paginatorInfo.lastPage + 1):
        index_query = {
            f"nations_{page}: nations": {
                "args": {"page": page, "first": 500},
                "data": ("id", "nation_name", "leader_name", "date")
            }
        }
        bulk_query.insert(index_query)


@plugin.command
@lightbulb.command("pw", "Politics and War commands.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def pw(ctx: RequiemContext) -> None:
    ...


@pw.child
@lightbulb.add_cooldown(10, 1, lightbulb.UserBucket)
@lightbulb.option("nation", "Name or ID of a nation to lookup.", autocomplete=True)
@lightbulb.command("nation",  "View information for a specified nation.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _nation(ctx: RequiemContext) -> None:
    response = await pwpy.get_query(queries.NATION_COMMAND)
    nation: pwpy.Nation = pwpy.Nation.convert(response["nations"]["data"][0])

    header_str = f"[{nation.nation_name}]({nation.url}) - [{nation.leader_name}]({nation.message_url})"

    embed = hikari.Embed(description=header_str, color=ctx.color)
    embed.add_field("Creation Date", value=nation.date.strftime("%b %d, %Y"), inline=True)

    if _alliance := nation.alliance:
        embed.add_field(name="Alliance", value=f"[{_alliance.name}]({_alliance.url})", inline=False)

    embed.add_field(name="Score", value=f"{round(nation.score, 2):,}", inline=True)
    embed.add_field(name="Color", value=nation.color.title(), inline=True)
    embed.add_field(name="Cities", value=f"[{len(nation.cities)}]({nation.city_manager_url})",inline=True)
    embed.add_field(name="Population", value=f"{nation.population:,}", inline=True)
    embed.add_field(name="Infra", value=f"{round(nation.total_infra, 2):,}", inline=True)
    embed.add_field(name="Land", value=f"{round(nation.total_land, 2):,}", inline=True)
    war_policy = nation.war_policy.value.replace("_", " ").title()
    embed.add_field(name="War Policy", value=war_policy, inline=True)
    dom_policy = nation.domestic_policy.value.replace("_", " ").title()
    embed.add_field(name="Domestic Policy", value=dom_policy, inline=True)
    min_score, max_score = nation.score_range
    strike_range_str = f"[{round(min_score, 2):,} - {round(max_score, 2):,}]({nation.war_range_url})"
    embed.add_field(name="Strike Range", value=strike_range_str)
    embed.add_field(name="Soldiers", value=f"{nation.soldiers:,}", inline=True)
    embed.add_field(name="Tanks", value=f"{nation.tanks:,}", inline=True)
    embed.add_field(name="Aircraft", value=f"{nation.aircraft:,}", inline=True)
    embed.add_field(name="Ships", value=f"{nation.ships:,}", inline=True)
    embed.add_field(name="Missiles", value=f"{nation.missiles:,}", inline=True)
    embed.add_field(name="Nukes", value=f"{nation.nukes:,}", inline=True)
    embed.set_image(nation.flag)

    await ctx.respond(embed=embed)


@_nation.autocomplete("nation")
async def nation_autocomplete(
    option: hikari.AutocompleteInteractionOption,
    interaction: hikari.AutocompleteInteraction
) -> list:
    response = NATIONS.search(option.value, interaction.user.id)
    return response
