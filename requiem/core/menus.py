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


from discord.ext import menus, commands

import discord


class UniversalPaginator(menus.Menu):
    """
    Embed page menu built using dpy menus lib.
    """

    def __init__(self, pages, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = pages
        self.current_page = 0

    async def send_initial_message(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> discord.Message:
        """
        Sends the first page.
        """
        page = self.pages[0]
        return await channel.send(embed=page)

    async def change_page(self) -> None:
        """
        Updates the embed with the selected page.
        """
        embed = self.pages[self.current_page]
        await self.message.edit(embed=embed)

    @menus.button("⏮")
    async def jump_to_first(self, _) -> None:
        """
        Jumps to the first page.
        """
        self.current_page = 0
        await self.change_page()

    @menus.button("◀")
    async def previous_page(self, _) -> None:
        """
        Jumps back one page.
        """
        if self.current_page:
            self.current_page -= 1
            await self.change_page()

    @menus.button("❎")
    async def close(self, _) -> None:
        """
        Closes the paginator
        """
        self.stop()

    @menus.button("▶")
    async def next_page(self, _) -> None:
        """
        Jumps forward one page.
        """
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await self.change_page()

    @menus.button("⏭")
    async def last_page(self, _) -> None:
        """
        Jumps to last page.
        """
        self.current_page = len(self.pages) - 1
        await self.change_page()
