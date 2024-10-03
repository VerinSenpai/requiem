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
from requiem.core.app import RequiemApp

import lightbulb
import hikari
import time


plugin = lightbulb.Plugin("requiem_basic")


@plugin.command
@lightbulb.command("ping", "View current ping times for Requiem.")
@lightbulb.implements(lightbulb.SlashCommand, lightbulb.PrefixCommand)
async def ping(ctx: lightbulb.Context):
    start = time.monotonic()
    embed = hikari.Embed(title="Pinging!")
    message = await ctx.respond(embed=embed)
    heartbeat = round(ctx.bot.heartbeat_latency * 1000, 2)
    ack = int((time.monotonic() - start) * 1000)
    embed.title = None
    embed.add_field(name="Heartbeat", value=f"{heartbeat}ms")
    embed.add_field(name="ACK", value=f"{ack}ms")
    await message.edit(embed=embed)


@plugin.command
@lightbulb.command("about", "View Requiem description and version information.")
@lightbulb.implements(lightbulb.SlashCommand,  lightbulb.PrefixCommand)
async def about(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(description=ctx.app.application.description)
    embed.add_field(name="Requiem Version", value=__version__, inline=True)
    embed.add_field(name="Hikari Version", value=hikari.__version__, inline=True)
    embed.add_field(name="Lightbulb Version", value=lightbulb.__version__, inline=True)
    await ctx.respond(embed=embed)


def load(bot: RequiemApp) -> None:
    bot.add_plugin(plugin)


def unload(bot: RequiemApp) -> None:
    bot.remove_plugin(plugin)
