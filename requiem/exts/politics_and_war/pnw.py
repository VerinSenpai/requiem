# This is part of Requiem
# Copyright (C) 2020  Verin Senpai

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


from requiem.core.context import RequiemContext
from requiem.core.config import PnWConfig

import lightbulb
import pwpy
import hikari


plugin = lightbulb.Plugin("PW")
pw_config: PnWConfig | None = None


@plugin.command
@lightbulb.command("pw", "Politics and War commands.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def pw(ctx: RequiemContext) -> None:
    ...


@pw.child
@lightbulb.add_cooldown(10, 1, lightbulb.UserBucket)
@lightbulb.command("nation", "View information for a specified nation.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def nation(ctx: RequiemContext) -> None:
    query = {
        "model": "nations",
        "args": {"id": 34904},
        "query": {
            "data": (
                {"alliance": ("name", "id")},
                {"cities": ("infrastructure", "land")},
                "nation_name",
                "leader_name",
                "id",
                "num_cities",
                "population",
                "domestic_policy",
                "war_policy",
                "soldiers",
                "tanks",
                "aircraft",
                "ships",
                "missiles",
                "nukes",
                "flag",
                "score",
                "date",
                "color"
            ),
        }
    }

    response = await pwpy.api.get_query(query, pw_config.api_key)
    _nation = pwpy.models.Nation(response["nations"]["data"][0])

    infra = land = 0
    for city in _nation.cities:
        infra += city.infra
        land += city.land

    nation_url: str = f"{pwpy.urls.NATION_PAGE}/id={_nation.id}"
    message_url: str = f"{pwpy.urls.MESSAGE_PAGE}/receiver={_nation.leader_name}".replace(" ", "%20")
    embed = hikari.Embed(
        description=f"[{_nation.nation_name}]({nation_url}) - [{_nation.leader_name}]({message_url})",
        color=ctx.color
    )

    if _nation.alliance is not None:
        alliance_url = f"{pwpy.urls.ALLIANCE_PAGE}/id={_nation.alliance.id}"
        embed.add_field(name="Alliance", value=f"[{_nation.alliance.name}]({alliance_url})")

    score = _nation.score
    embed.add_field(name="Score", value=str(score), inline=True)
    min_range, max_range = pwpy.utils.score_range(score)
    range_url = (f"{pwpy.urls.WARS_PAGE}&keyword={score}&cat=war_range"
                 f"&ob=score&od=ASC&beige=true&vmode=false&openslots=true")
    embed.add_field(
        name="Strike Range",
        value=f"[{round(min_range, 2)} - {round(max_range, 2)}]({range_url})",
        inline=True
    )

    cities_url = f"{pwpy.urls.CITY_MANAGER_PAGE}&l={_nation}"
    embed.add_field(name="Cities", value=f"[{_nation.num_cities}]({cities_url})", inline=True)
    embed.add_field(name="Population", value=f'{_nation.population:,}', inline=True)
    embed.add_field(name="Infra", value=str(infra), inline=True)
    embed.add_field(name="Land", value=str(land), inline=True)
    embed.add_field(name="Color", value=_nation.color, inline=True)
    embed.add_field(name="Domestic Policy", value=_nation.domestic_policy, inline=True)
    embed.add_field(name="War Policy", value=_nation.war_policy, inline=True)
    embed.add_field(name="Soldiers", value=f'{_nation.soldiers:,}', inline=True)
    embed.add_field(name="Tanks", value=f'{_nation.tanks:,}', inline=True)
    embed.add_field(name="Aircraft", value=f'{_nation.aircraft:,}', inline=True)
    embed.add_field(name="Ships", value=f'{_nation.ships:,}', inline=True)
    embed.add_field(name="Missiles", value=f'{_nation.missiles:,}', inline=True)
    embed.add_field(name="Nukes", value=f'{_nation.nukes:,}', inline=True)
    embed.set_image(_nation.flag)

    await ctx.respond(embed=embed)

