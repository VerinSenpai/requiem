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

import aiohttp
import discord
import nekos

from discord.ext import commands


class VerinsLunchbox(commands.Cog, name="verins lunchbox"):
    """
    Various joke and meme commands. Cat girls?.
    """

    @commands.command(brief="Cat girl pics?", aliases=("neko",))
    @commands.cooldown(1, 2.5)
    async def catgirl(self, ctx: commands.Context) -> None:
        """
        Shows a random cat girl picture.
        """
        embed = discord.Embed(color=discord.Colour.purple())
        embed.set_footer(text="Results provided by https://Nekos.Life")
        embed.set_image(url=nekos.img("neko"))
        await ctx.send(embed=embed)

    @commands.command(brief="Random cat facts.")
    @commands.cooldown(1, 2.5)
    async def catfact(self, ctx: commands.Context) -> None:
        """
        Provides a random cat fact.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get("https://catfact.ninja/fact") as session:
                data = await session.json(content_type="application/json")

        embed = discord.Embed(description=data["fact"], color=discord.Colour.purple())
        embed.set_footer(text="Results Provided By https://catfact.ninja/facts")
        await ctx.send(embed=embed)

    @commands.command(brief="Chuck Norris.")
    @commands.cooldown(1, 2.5)
    async def chucknorris(self, ctx: commands.Context) -> None:
        """
        Chuck Norris was here.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get("https://api.chucknorris.io/jokes/random") as session:
                data = await session.json(content_type="application/json")

        embed = discord.Embed(description=data["value"], color=discord.Colour.purple())
        embed.set_footer(text="Results Provided By https://api.chucknorris.io/")
        await ctx.send(embed=embed)


def setup(bot):
    """
    Setup function required by dpy. Adds VerinsLunchbox as a cog.
    """
    bot.add_cog(VerinsLunchbox())
