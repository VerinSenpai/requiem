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


import lightbulb
import hikari
import aiohttp


async def session_wrap(url: str) -> dict:
    """
    Creates a one use session async session and returns the response json.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(content_type="application/json")


async def failsafe_neko(reference: str, ctx: lightbulb.Context) -> None:
    """
    A function to assist in sending of nekos.life payloads and handling NothingFound errors.
    """
    embed = hikari.Embed()
    data = await session_wrap(f"https://nekos.life/api/v2/img/{reference}")
    embed.set_image(data["url"])
    await ctx.respond(embed=embed)


@lightbulb.command("neko", "Photos of cat girls. My most useful feature.")
@lightbulb.implements(lightbulb.SlashCommand)
async def neko(ctx: lightbulb.Context):
    await failsafe_neko("neko", ctx)


@lightbulb.command("foxgirl", "Second only to cat girls, we've got photos of fox girls.")
@lightbulb.implements(lightbulb.SlashCommand)
async def foxgirl(ctx: lightbulb.Context):
    await failsafe_neko("fox_girl", ctx)


@lightbulb.command("catfact", "Learn yourself a cat fact.")
@lightbulb.implements(lightbulb.SlashCommand)
async def catfact(ctx: lightbulb.Context):
    data = await session_wrap("https://catfact.ninja/fact")
    embed = hikari.Embed(description=data["fact"])
    embed.set_footer(text="Results provided by https://catfact.ninja/fact")
    await ctx.respond(embed=embed)



