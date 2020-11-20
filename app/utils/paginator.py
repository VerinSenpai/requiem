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


import contextlib
import discord
import asyncio

from discord.ext import commands


class Paginator:
    """
    Custom Requiem specific paginator. I hate this.
    """

    def __init__(
        self, ctx: commands.Context, destination: discord.abc.Messageable, pages
    ) -> None:
        self.ctx = ctx
        self.bot = ctx.bot
        self.destination = destination
        self.pages = pages

    async def run(self) -> None:
        """
        Runs the paginator. Self explanatory I think.
        """
        page = 0
        controls = ("⏮", "◀", "❎", "▶", "⏭")

        with contextlib.suppress(
            discord.Forbidden, discord.NotFound, asyncio.TimeoutError
        ):
            message = await self.destination.send(embed=self.pages[0])

            if len(self.pages) == 1:
                return

            for reaction in controls:
                await message.add_reaction(reaction)

            while True:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60,
                    check=lambda r, u: (
                        u.id == self.ctx.author.id
                        and r.emoji in controls
                        and r.message.id == message.id
                    ),
                )

                with contextlib.suppress(discord.Forbidden):
                    await message.remove_reaction(str(reaction.emoji), user)

                if reaction.emoji == controls[0]:
                    page = 0

                elif reaction.emoji == controls[1]:
                    page = page - 1 if page else 0

                elif reaction.emoji == controls[2]:
                    return await message.delete()

                elif reaction.emoji == controls[3]:
                    page = (
                        page + 1 if page < len(self.pages) - 1 else len(self.pages) - 1
                    )

                elif reaction.emoji == controls[4]:
                    page = len(self.pages) - 1

                await message.edit(embed=self.pages[page])
