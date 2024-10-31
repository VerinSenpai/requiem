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

from requiem.core.impl import RequiemContext, RequiemPlugin
from requiem.core.models import AutoCompleteIndex
from requiem.exts.politics_and_war import queries, background
from lightbulb.ext import tasks

import pwpy
import lightbulb
import hikari
import logging


_LOGGER = logging.getLogger("pw.commands")


plugin = RequiemPlugin("pw")


NATIONS = AutoCompleteIndex()
ALLIANCES = AutoCompleteIndex()


async def setup():
    api_key: str | None = plugin.config.pw.api_key

    if api_key:
        pwpy.set_global_key(api_key)

        try:
            await pwpy.get_query(queries.GAME_DATE)

            return

        except pwpy.QueryKeyError:
            _LOGGER.warning("provided api_key is invalid! pw commands and features will be unavailable!")

    else:
        _LOGGER.warning("api_key not provided! pw commands and features will be unavailable!")

    perform_indexing.stop()


@tasks.task(m=10)
async def perform_indexing(event: hikari.StartedEvent):



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
async def nation(ctx: RequiemContext) -> None:
    response = await background.SESSION.get_query(queries.NATION_COMMAND)
    _nation: Nation = Nation.convert(response["nations"]["data"][0])

    header_str = f"[{_nation.nation_name}]({_nation.url}) - [{_nation.leader_name}]({_nation.message_url})"

    embed = hikari.Embed(description=header_str, color=ctx.color)
    embed.add_field("Creation Date", value=_nation.date.strftime("%b %d, %Y"), inline=True)

    if _alliance := _nation.alliance:
        embed.add_field(name="Alliance", value=f"[{_alliance.name}]({_alliance.url})", inline=False)

    embed.add_field(name="Score", value=f"{round(_nation.score, 2):,}", inline=True)
    embed.add_field(name="Color", value=_nation.color.title(), inline=True)
    embed.add_field(name="Cities", value=f"[{len(_nation.cities)}]({_nation.city_manager_url})",inline=True)
    embed.add_field(name="Population", value=f"{_nation.population:,}", inline=True)
    embed.add_field(name="Infra", value=f"{round(_nation.total_infra, 2):,}", inline=True)
    embed.add_field(name="Land", value=f"{round(_nation.total_land, 2):,}", inline=True)
    war_policy = _nation.war_policy.value.replace("_", " ").title()
    embed.add_field(name="War Policy", value=war_policy, inline=True)
    dom_policy = _nation.domestic_policy.value.replace("_", " ").title()
    embed.add_field(name="Domestic Policy", value=dom_policy, inline=True)
    min_score, max_score = _nation.score_range
    strike_range_str = f"[{round(min_score, 2):,} - {round(max_score, 2):,}]({_nation.war_range_url})"
    embed.add_field(name="Strike Range", value=strike_range_str)
    embed.add_field(name="Soldiers", value=f"{_nation.soldiers:,}", inline=True)
    embed.add_field(name="Tanks", value=f"{_nation.tanks:,}", inline=True)
    embed.add_field(name="Aircraft", value=f"{_nation.aircraft:,}", inline=True)
    embed.add_field(name="Ships", value=f"{_nation.ships:,}", inline=True)
    embed.add_field(name="Missiles", value=f"{_nation.missiles:,}", inline=True)
    embed.add_field(name="Nukes", value=f"{_nation.nukes:,}", inline=True)
    embed.set_image(_nation.flag)

    await ctx.respond(embed=embed)


@nation.autocomplete("nation")
async def nation_autocomplete(
    option: hikari.AutocompleteInteractionOption,
    interaction: hikari.AutocompleteInteraction
) -> list:
    response = NATIONS.search(option.value, interaction.user.id)
    return response
