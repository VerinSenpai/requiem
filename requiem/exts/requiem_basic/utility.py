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


from requiem import __discord__, __version__, __repo_url__
from requiem.core.context import RequiemContext
from datetime import datetime

import lightbulb
import hikari


plugin = lightbulb.Plugin("Utility")


@plugin.command
@lightbulb.command("util", "Utility commands.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def util(ctx: RequiemContext):
    ...


@util.child
@lightbulb.command("ping", "View current ping times for Requiem.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ping(ctx: RequiemContext):
    start_time = datetime.now()
    embed = hikari.Embed(title="Pinging!", color=ctx.color)
    message = await ctx.respond(embed=embed)
    heartbeat = round(ctx.bot.heartbeat_latency * 1000, 2)
    ack = int((datetime.now() - start_time).microseconds / 1000)
    embed.title = None
    embed.add_field(name="Heartbeat", value=f"{heartbeat}ms")
    embed.add_field(name="ACK", value=f"{ack}ms")
    await message.edit(embed=embed)


@util.child
@lightbulb.command("about", "View Requiem description and version information.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def about(ctx: RequiemContext) -> None:
    bot_app = ctx.app.application

    embed = (
        hikari.Embed(title=f"Requiem Project", url=__repo_url__, description=bot_app.description, color=ctx.color)
        .add_field(name="Requiem Version", value=__version__, inline=True)
        .add_field(name="Hikari Version", value=hikari.__version__, inline=True)
        .add_field(name="Lightbulb Version", value=lightbulb.__version__, inline=True)
        .set_thumbnail(ctx.app.application.icon_url)
    )

    await ctx.respond(embed=embed)
