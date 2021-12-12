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
import nekos


async def failsafe_neko(reference: str, ctx: lightbulb.Context) -> None:
    """
    A function to assist in sending of nekos.life payloads and handling NothingFound errors.
    """
    embed = hikari.Embed()
    attempts = 0

    while attempts < 3:
        try:
            image = nekos.img(reference)
            embed.set_image(image)
            break

        except nekos.errors.NothingFound:
            pass

    if attempts == 3:
        embed.description = "There was a problem connecting to nekos.life!"

    await ctx.respond(embed=embed)


@lightbulb.command("neko", "Photos of cat girls. My most useful feature.")
@lightbulb.implements(lightbulb.SlashCommand)
async def neko(ctx: lightbulb.Context):
    await failsafe_neko("neko", ctx)


@lightbulb.command("foxgirl", "Second only to cat girls, we've got photos of fox girls.")
@lightbulb.implements(lightbulb.SlashCommand)
async def foxgirl(ctx: lightbulb.Context):
    await failsafe_neko("fox_girl", ctx)
