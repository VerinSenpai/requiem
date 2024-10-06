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

import lightbulb
import hikari


plugin = lightbulb.Plugin("Debug")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("error", "Raises a random exception to test error handling.")
@lightbulb.implements(lightbulb.PrefixCommand)
async def error(ctx: RequiemContext) -> None:
    await ctx.respond("raising an exception...")
    raise Exception("This is a test")


@plugin.command
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.command("terminate", "Exit Requiem.")
@lightbulb.implements(lightbulb.PrefixCommand)
async def terminate(ctx: RequiemContext):
    embed = hikari.Embed(title="Requiem is shutting down!", color=ctx.color)
    await ctx.respond(embed=embed)
    await ctx.app.close()
