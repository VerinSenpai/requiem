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


from discord.ext import commands
from core import client

import discord
import nekos


class VerinsLunchbox(commands.Cog, name="verins lunchbox"):
    """
    Memes, cat girls, and dog pics. What more could you want?
    """

    @commands.command(brief="Cat girl pics?", aliases=("neko",))
    @commands.cooldown(1, 2.5)
    async def catgirl(self, ctx: commands.Context) -> None:
        """
        Provides a random cat girl pic.
        Verin's favorite command.
        Obviously.
        """
        embed = discord.Embed(colour=ctx.colour)
        embed.set_footer(text="Results provided by https://Nekos.Life")
        embed.set_image(url=nekos.img("neko"))
        await ctx.send(embed=embed)


def setup(bot: client.Requiem) -> None:
    bot.add_cog(VerinsLunchbox())
