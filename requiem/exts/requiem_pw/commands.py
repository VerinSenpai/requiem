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
from requiem.core.models import AutoCompleteIndex, NationStore
from requiem.exts.requiem_pw import utils
from lightbulb.ext import tasks
from tortoise.expressions import Q

import typing as t
import pwpy
import lightbulb
import hikari
import logging


_LOGGER = logging.getLogger("pw.commands")


plugin = RequiemPlugin("pw")


READY: bool = False
FAILED: bool = False


def ready_check(ctx) -> bool:
    if FAILED:
        raise lightbulb.CheckFailure("There was an issue setting up! PW commands and features are unavailable!")

    elif not READY:
        raise lightbulb.CheckFailure("RequiemPW has not finished setting up! Please try again in a few minutes!")

    return True


plugin.add_checks(lightbulb.Check(ready_check))


@tasks.task(s=1, max_executions=1)
async def setup():
    global READY, FAILED

    api_key: str | None = plugin.config.pw.api_key

    if api_key:
        pwpy.set_global_key(api_key)

        try:
            await pwpy.get_query({"game_info": "game_date"})
            READY = True
            build_nations_index.start()
            return

        except pwpy.QueryKeyError:
            _LOGGER.warning("provided api_key is invalid! pw commands and features will be unavailable!")

    else:
        _LOGGER.warning("api_key not provided! pw commands and features will be unavailable!")

    FAILED = True


NATIONS_INDEX = AutoCompleteIndex()


@tasks.task(m=10)
async def build_nations_index():
    pages_query = {"nations": {"args": {"first": 500, "page": 1}, "paginatorInfo": "lastPage"}}
    nations_pages = (await pwpy.get_query(pages_query, parse=True)).nations.paginatorInfo.lastPage

    bulk_query = pwpy.BulkQuery()

    for page in range(1, nations_pages + 1):
        page_query = {
            f"page_{page}: nations": {
                "args": {"first": 500, "page": page},
                "data": ("id", "nation_name", "leader_name", "date")
            }
        }

        bulk_query.insert(page_query)

    nations = (
        pwpy.Nation.convert(nation)
        for query in await bulk_query.get()
        for group in query.values()
        for nation in group["data"]
    )

    updated = []

    for nation in nations:
        stored, created = await NationStore.get_or_create(
            id=nation.id,
            defaults={
                "nation_name": nation.nation_name.lower(),
                "leader_name": nation.leader_name.lower(),
                "date": nation.date,
                "original_date": nation.date
            }
        )

        NATIONS_INDEX.insert(nation.nation_name)

        if created:
            continue

        if any((
            nation.nation_name.lower() != stored.nation_name,
            nation.leader_name.lower() != stored.leader_name,
            nation.date != stored.date
        )):
            stored.nation_name = nation.nation_name.lower()
            stored.leader_name = nation.leader_name.lower()
            stored.date = nation.date
            updated.append(stored)

    if updated:
        await NationStore.bulk_update(updated, fields=["nation_name", "leader_name", "date"])

    NATIONS_INDEX.update()


@plugin.command
@lightbulb.command("pw", "Politics and War commands.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def pw(ctx: RequiemContext) -> None:
    ...


@pw.child
@lightbulb.option(
    "nation",
    "Name, ID, or leader of a nation.",
    type=str,
    autocomplete=True,
    required=False
)
@lightbulb.option(
    "discord",
    "Discord user linked with a nation.",
    type=hikari.User,
    required=False
)
@lightbulb.command("nation",  "View information for a specified nation.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def _nation(ctx: RequiemContext, nation: str = None, discord: hikari.User = None) -> None:
    if all((nation, discord)):
        raise lightbulb.CheckFailure("Please pass either nation or discord, not both!")

    search_filter = utils.nations_filter(str(nation or discord).lower())
    nation_lookup = await NationStore.get_or_none(search_filter)

    if nation_lookup is None:
        raise lightbulb.CheckFailure("No nation matching that query could be found!")

    query = {"nations": {"args": {"id": nation_lookup.id}, "data": (
        {"alliance": ("id", "name")}, {"cities": ("infrastructure", "land", "powered")},
        "id",  "nation_name",  "leader_name", "score", "population", "color", "war_policy", "domestic_policy",
        "flag", "date", "last_active", "soldiers", "tanks", "aircraft", "ships", "missiles", "nukes"
    )}}

    try:
        nation = (await pwpy.get_query(query, parse=True)).nations.data[0]

    except IndexError:
        raise lightbulb.CheckFailure("The nation you are requesting no longer exists!")

    header_str = f"[{nation.nation_name}]({nation.url}) - [{nation.leader_name}]({nation.message_url})"
    embed = hikari.Embed(description=header_str, color=ctx.color)
    embed.add_field("Creation Date", value=nation.date.strftime("%b %d, %Y"))
    embed.add_field("Last Active", value=utils.last_active_str(nation.last_active))

    if alliance := nation.alliance:
        embed.add_field(name="Alliance", value=f"[{alliance.name}]({alliance.url})")

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

    NATIONS_INDEX.record(ctx.user.id, nation.nation_name)

    await ctx.respond(embed=embed)


@_nation.autocomplete("nation")
async def nation_autocomplete(
    option: hikari.AutocompleteInteractionOption,
    interaction: hikari.AutocompleteInteraction
) -> list:
    return NATIONS_INDEX.search(option.value, interaction.user.id, limit=10)
