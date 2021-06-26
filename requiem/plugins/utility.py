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


from core import context, client
from discord.ext import commands

import discord
import time


class Utility(commands.Cog, name="utility"):
    """
    Informational tools for users, guilds, and Requiem.
    """

    @commands.command(brief="View my heartbeat and rest pings.")
    async def ping(self, ctx: context.Context) -> None:
        """
        Provides the current Heartbeat and Rest pings.

        Heartbeat: Time taken between sending a heartbeat and receiving an acknowledgement.
        Rest: Time taken between performing a request and receiving a response.
        """
        start = time.monotonic()
        await ctx.fetch_message(ctx.message.id)
        end = time.monotonic()

        gateway = int((end - start) * 1000)
        heartbeat = int(ctx.bot.latency * 1000)

        if heartbeat >= 150:
            colour = discord.Colour.red()
        elif heartbeat > 70 < 150:
            colour = discord.Colour.gold()
        else:
            colour = discord.Colour.green()

        embed = discord.Embed(colour=colour)
        embed.add_field(name="Heartbeat", value=f"{heartbeat}ms", inline=False)
        embed.add_field(name="Rest", value=f"{gateway}ms", inline=False)
        await ctx.send(embed=embed)


def setup(bot: client.Requiem) -> None:
    bot.add_cog(Utility())
