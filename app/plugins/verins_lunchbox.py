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
from core.bot import Requiem


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
        embed = discord.Embed(colour=discord.Colour.purple())
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
            async with csess.get("https://catfact.ninja/fact") as response:
                data = await response.json(content_type="application/json")

        embed = discord.Embed(description=data["fact"], colour=discord.Colour.purple())
        embed.set_footer(text="Results Provided By https://catfact.ninja/facts")
        await ctx.send(embed=embed)

    @commands.command(brief="Chuck Norris.")
    @commands.cooldown(1, 2.5)
    async def chucknorris(self, ctx: commands.Context) -> None:
        """
        Chuck Norris was here.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get("https://api.chucknorris.io/jokes/random") as response:
                data = await response.json(content_type="application/json")

        embed = discord.Embed(description=data["value"], colour=discord.Colour.purple())
        embed.set_footer(text="Results Provided By https://api.chucknorris.io/")
        await ctx.send(embed=embed)

    @commands.command(brief="Fox girl pics?")
    @commands.cooldown(1, 2.5)
    async def foxgirl(self, ctx: commands.Context) -> None:
        """
        Shows a random fox girl picture. Almost as good as cat girls ngl.
        """
        embed = discord.Embed(colour=discord.Colour.purple())
        embed.set_footer(text="Results provided by https://Nekos.Life")
        embed.set_image(url=nekos.img("fox_girl"))
        await ctx.send(embed=embed)

    @commands.command(brief="Random dad jokes.")
    @commands.cooldown(1, 2.5)
    async def dadjoke(self, ctx: commands.Context) -> None:
        """
        I'm not good at dad jokes.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get(
                "https://icanhazdadjoke.com/", headers={"Accept": "application/json"}
            ) as response:
                data = await response.json(content_type="application/json")

        embed = discord.Embed(description=data["joke"], colour=discord.Colour.purple())
        embed.set_footer(text="Results Provided By https://icanhazdadjoke.com/")
        await ctx.send(embed=embed)

    @commands.command(brief="Random doggo pics.")
    @commands.cooldown(1, 2.5)
    async def doggo(self, ctx: commands.Context) -> None:
        """
        Sends a random dog pic.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get("https://dog.ceo/api/breeds/image/random") as result:
                data = await result.json()

        embed = discord.Embed(colour=discord.Colour.purple())
        embed.set_image(url=data["message"])
        embed.set_footer(text="Results Provided By https://dog.ceo/api")
        await ctx.send(embed=embed)

    @commands.command(brief="Geek jokes.")
    @commands.cooldown(1, 2.5)
    async def geeket(self, ctx: commands.Context) -> None:
        """
        Sends a random geek joke.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get(
                "https://geek-jokes.sameerkumar.website/api"
            ) as result:
                data = await result.json(content_type="application/json")

        embed = discord.Embed(description=data, colour=discord.Colour.purple())
        embed.set_footer(
            text="Results Provided By https://geek-jokes.sameerkumar.website/api"
        )
        await ctx.send(embed=embed)

    @commands.command(brief="Random number facts.")
    @commands.cooldown(1, 2.5)
    async def numberfact(self, ctx: commands.Context) -> None:
        """
        Sends a random number fact.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get("http://numbersapi.com/random") as result:
                data = await result.read()

        embed = discord.Embed(
            description=data.decode("utf-8"), colour=discord.Colour.purple()
        )
        embed.set_footer(text="Results Provided By https://numbersapi.com/")
        await ctx.send(embed=embed)

    @commands.command(brief="TRBMB. I don't know.")
    @commands.cooldown(1, 2.5)
    async def trbmb(self, ctx: commands.Context) -> None:
        """
        That really beans my beans.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get("https://api.chew.pro/trbmb") as result:
                data = await result.json(content_type="application/json")

        embed = discord.Embed(description=data[0], colour=discord.Colour.purple())
        embed.set_footer(text="Results Provided By https://api.chew.pro/trbmb")
        await ctx.send(embed=embed)

    @commands.command(brief="Useless facts.")
    @commands.cooldown(1, 2.5)
    async def uselessfact(self, ctx: commands.Context) -> None:
        """
        Sends a random useless fact.
        """
        async with aiohttp.ClientSession() as csess:
            async with csess.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
            ) as result:
                data = await result.json(content_type="application/json")
        fact, source_url, source = data["text"], data["source_url"], data["source"]

        embed = discord.Embed(colour=discord.Colour.purple())
        embed.add_field(name="Fact", value=fact, inline=False)
        embed.add_field(name="Source", value=f"[{source}]({source_url})", inline=False)
        embed.set_footer(text="Results Provided By uselessfacts.jsph.pl")
        await ctx.send(embed=embed)


def setup(bot: Requiem) -> None:
    bot.add_cog(VerinsLunchbox())
