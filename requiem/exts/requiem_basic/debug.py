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
plugin.add_checks(lightbulb.owner_only)


@plugin.command
@lightbulb.command("debug", "Commands for testing, debugging, and development.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def debug(ctx: RequiemContext):
    ...


@debug.child
@lightbulb.option(
    name="type",
    description="Type of exception to be raised",
    type=int,
    choices=(
        hikari.CommandChoice(name="Unhandled", value=0),
        hikari.CommandChoice(name="CommandIsOnCooldown", value=1),
        hikari.CommandChoice(name="NotOwner", value=2),
        hikari.CommandChoice(name="NSFWChannelOnly", value=3),
        hikari.CommandChoice(name="HumanOnly", value=4)
    )
)
@lightbulb.command("error", "Raises a random exception to test error handling.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def error(ctx: RequiemContext) -> None:
    exceptions = (
        Exception("Test of general exception handling."),
        lightbulb.CommandIsOnCooldown("CommandIsOnCooldown raised. You shouldn't see this!", retry_after=10),
        lightbulb.NotOwner("NotOwner raised. You shouldn't see this!"),
        lightbulb.NSFWChannelOnly("NSFWChannelOnly raised. You shouldn't see this!"),
        lightbulb.HumanOnly("HumanOnly raised. You shouldn't see this!")
    )

    exception = exceptions[ctx.options["type"]]
    await ctx.respond(embed=hikari.Embed(description=f"raising exception '{type(exception)}'!", color=ctx.color))
    raise exception


@debug.child
@lightbulb.command("terminate", "Exit Requiem.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def terminate(ctx: RequiemContext):
    await ctx.respond(embed=hikari.Embed(title="Requiem is shutting down!", color=ctx.color))
    await ctx.app.close()
