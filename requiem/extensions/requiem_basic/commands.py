# This is part of Requiem
# Copyright (C) 2020  God Empress Verin

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

import datetime

import lightbulb
import hikari
import time
import __init__


@lightbulb.command("ping", "View current ping times for Requiem.")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context):
    embed = hikari.Embed(description="Pinging...")

    start = time.monotonic()
    message = await ctx.respond(embed=embed)

    ack = int((time.monotonic() - start) * 1000)
    heartbeat = round(ctx.bot.heartbeat_latency * 1000, 2)

    embed.description = ""
    embed.add_field(name="Heartbeat", value=f"{heartbeat}ms")
    embed.add_field(name="ACK", value=f"{ack}ms")

    await message.edit(embed=embed)


@lightbulb.command("about", "View information about Requiem.")
@lightbulb.implements(lightbulb.SlashCommand)
async def about(ctx: lightbulb.Context) -> None:
    bot = ctx.bot
    embed = hikari.Embed()

    description = """
    Requiem is a specially crafted discord bot built to provide the largest
    number of tools and resources for the politics and war community in a
    convenient and easy to use package. Requiem is, always has been, and
    always will be free to use for everyone. Have a feature request or an
    issue to report? Consider dropping by the Requiem [support server](https://discord.gg/uTXdx7J)!
    Want to take a look at my inner workings or fork Requiem? Take a look
    at my [repo](https://github.com/GodEmpressVerin/requiem)!
    """

    embed.add_field(name="Requiem Version", value=__init__.__version__, inline=True)
    embed.add_field(name="Hikari Version", value=hikari.__version__, inline=True)
    embed.add_field(name="Lightbulb Version", value=lightbulb.__version__, inline=True)
    embed.add_field(name="Commands Executed", value=bot.cmds_run + 1, inline=True)
    embed.add_field(name="Uptime", value=bot.uptime, inline=True)
    embed.add_field(name="About Requiem", value=description)

    await ctx.respond(embed=embed)


@lightbulb.option(
    "user",
    "A user to be looked up. Leave blank to lookup yourself.",
    type=hikari.Member,
    required=False
)
@lightbulb.command("avatar", "View the avatar of a specified user.")
@lightbulb.implements(lightbulb.SlashCommand)
async def avatar(ctx: lightbulb.Context) -> None:
    member = ctx.options.user

    if not member:
        member = ctx.member

    embed = hikari.Embed()
    embed.set_thumbnail(member.avatar_url)

    await ctx.respond(embed=embed)


@lightbulb.option(
    "user",
    "A user to be looked up. Leave blank to lookup yourself.",
    type=hikari.Member,
    required=False
)
@lightbulb.command("userinfo", "View info about a specified user.")
@lightbulb.implements(lightbulb.SlashCommand)
async def user(ctx: lightbulb.Context):
    member = ctx.options.user

    if not member:
        member = ctx.member

    embed = hikari.Embed()

    embed.add_field(name="Username", value=member.username)

    if member.nickname and member.nickname != member.username:
        embed.add_field(name="Nickname", value=member.nickname)

    embed.add_field(name="Snowflake", value=str(member.id))

    created_at = member.created_at.strftime("%A %B %d, %Y")
    embed.add_field(name="Account Created On", value=created_at)

    joined_at = member.joined_at.strftime("%A %B %d, %Y")
    embed.add_field(name="Member Joined On:", value=joined_at)

    embed.add_field(name="Roles", value=str(len(member.role_ids)))

    top_role = member.get_top_role()
    embed.add_field(name="Top Role", value=str(top_role))

    embed.set_thumbnail(member.avatar_url)

    await ctx.respond(embed=embed)
