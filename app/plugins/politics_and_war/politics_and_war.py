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


import discord
import typing
import timeago

from datetime import datetime, timezone, timedelta
from .utils import nation_lookup, alliance_lookup
from discord.ext import commands, tasks
from .backend import Backend


base_url = "https://politicsandwar.com"


class PoliticsAndWar(Backend, commands.Cog, name="politics and war"):
    """
    Various informational and utility commands for Politics and War.
    """

    @commands.group(aliases=["pwna"], brief="View a given nation.")
    @commands.cooldown(1, 2.5)
    async def pwnation(
        self, ctx: commands.Context, *, target: typing.Union[discord.User, str] = None
    ) -> None:
        """
        View information about a nation.

        You can look a nation up by its id, name, or a discord user (if they've linked themselves to their nation)
        If you don't specify a target, a lookup is performed for a nation linked to your discord.
        """
        target = target or ctx.author.id

        if isinstance(target, discord.User):
            target = target.id

        entry = await nation_lookup(target)

        if entry:
            name = (
                f"{entry.name} (formerly {entry.prev_name})"
                if entry.prev_name
                else entry.name
            )
            leader = (
                f"{entry.leader} (formerly {entry.leader})"
                if entry.prev_leader
                else entry.leader
            )

            name_url = f"[{name.title()}]({base_url}/nation/id={entry.id})"
            leader_url = f"[{leader.title()}]({base_url}/inbox/message/receiver={leader.replace(' ', '+')})"
            embed = discord.Embed(description=f"{name_url} - {leader_url}", colour=discord.Colour.purple())

            if entry.deleted:
                embed.add_field(
                    name="Deleted Nation",
                    value="You are viewing a nation that no longer exists.",
                    inline=False,
                )

            if entry.reroll:
                embed.add_field(
                    name="Re-roll",
                    value="You are viewing a nation that has re-rolled.",
                    inline=False,
                )

            if entry.vmode_turns:
                embed.add_field(
                    name="Vacation Mode",
                    value=f"This nation is in vacation mode for {entry.vmode_turns} more turns.",
                    inline=False,
                )

            if entry.beige_turns:
                embed.add_field(
                    name="Beige",
                    value=f"This nation is on beige for {entry.beige_turns} more turns.",
                    inline=False,
                )

            if alliance := await alliance_lookup(entry.alliance):
                embed.add_field(name="Alliance", value=f"{alliance.name.title()} ({alliance.acronym})")
                embed.add_field(name="Position", value=f"{entry.alliance_position.title()}")
                embed.add_field(name="IRC/Discord", value=alliance.irc, inline=False)

            elif entry.alliance:
                embed.add_field(name="Alliance", value="Unknown Alliance", inline=False)

            embed.add_field(name="War Policy", value=entry.war_policy.title())
            embed.add_field(name="Domestic Policy", value=entry.dom_policy.title())
            embed.add_field(name="Color", value=entry.color.title())
            embed.add_field(name="Cities", value=str(entry.cities))
            embed.add_field(name="Score", value=f"{entry.score:,}")
            embed.add_field(name="Soldiers", value=f"{entry.soldiers:,}")
            embed.add_field(name="Tanks", value=f"{entry.tanks:,}")
            embed.add_field(name="Aircraft", value=f"{entry.aircraft:,}")
            embed.add_field(name="Ships", value=f"{entry.ships:,}")
            embed.add_field(name="Missiles", value=f"{entry.missiles:,}")
            embed.add_field(name="Nukes", value=f"{entry.nukes:,}")

            last_updated = timeago.format(entry.last_updated, datetime.now(tz=timezone.utc))
            embed.set_footer(text=f"Nation last updated {last_updated}")

        else:
            embed = discord.Embed(
                description="That nation does not exist.",
                colour=discord.Colour.purple(),
            )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PoliticsAndWar())
