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


from requiem import __version__, __repo_url__
from requiem.core.impl import RequiemContext, RequiemPlugin
from datetime import datetime

import platform
import lightbulb
import hikari


plugin = RequiemPlugin("util")


@plugin.command
@lightbulb.command("util", "Utility commands.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def util(ctx: RequiemContext) -> None:
    ...


@util.child
@lightbulb.command("ping", "View current ping times for Requiem.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ping(ctx: RequiemContext) -> None:
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
        .add_field(name="Python", value=f"{platform.python_version()} {platform.python_implementation()}", inline=True)
        .add_field(name="OS", value=platform.platform(), inline=True)
        .set_thumbnail(ctx.app.application.icon_url)
    )

    await ctx.respond(embed=embed)


@util.child
@lightbulb.command("runtime", "View current session information.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def runtime(ctx: RequiemContext) -> None:
    uptime = ctx.app.session_time
    uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m {(uptime.seconds % 60)}s"

    embed = (
        hikari.Embed(title="Session Information", color=ctx.color)
        .add_field(name="Uptime", value=uptime_str, inline=True)
        .add_field(name="Commands Executed", value=f"0", inline=True)
        .add_field(name="Exceptions Handled", value=f"0", inline=True)
        .add_field(name="Plugins Loaded", value=str(len(ctx.app.plugins)), inline=True)
        .add_field(name="Extensions Loaded", value=str(len(ctx.app.extensions)), inline=True)
    )

    await ctx.respond(embed=embed)
