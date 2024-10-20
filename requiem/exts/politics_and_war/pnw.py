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


plugin = lightbulb.Plugin("PW")
pw_config: PnWConfig | None = None


@plugin.command
@lightbulb.command("pw", "Politics and War commands.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def pw(ctx: RequiemContext) -> None:
    ...


@pw.child
@lightbulb.command("nation", "View information for a specified nation.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def nation(ctx: RequiemContext) -> None:
    query = {
        "model": "nations",
        "args": {"id": 34904},
        "fields": {
            "data": (
                "nation_name",
                {"alliance": ("name", "id")}
            )
        }
    }

    resp = await pwpy.api.get_query(query, pw_config.api_key)

    await ctx.respond(resp)
