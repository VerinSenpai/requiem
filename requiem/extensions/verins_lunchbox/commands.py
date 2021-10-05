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


from lightbulb import slash_commands

import hikari
import nekos


class Neko(slash_commands.SlashCommand):

    description = "Photos of cat girls. My most useful feature."

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        embed = hikari.Embed()

        try:
            image = nekos.img("neko")
            embed.set_image(image)

        except nekos.errors.NothingFound:
            embed.description = "There was a problem connecting to nekos.life!"

        await ctx.respond(embed=embed)


class FoxGirl(slash_commands.SlashCommand):

    description = "Second only to cat girls, we've got photos of fox girls."

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        embed = hikari.Embed()

        try:
            image = nekos.img("fox_girl")
            embed.set_image(image)

        except nekos.errors.NothingFound:
            embed.description = "There was a problem connecting to nekos.life!"

        await ctx.respond(embed=embed)
