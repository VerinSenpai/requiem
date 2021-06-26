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
from core import menus

import discord


class HelpCommand(commands.HelpCommand):
    """
    Custom Requiem specific help command.
    """

    async def command_callback(
        self, ctx: commands.Context, *, command: str = None
    ) -> None:
        """Overwrites command_callback to implement case_insensitive searching."""
        command = command.lower() if command else command
        await super().command_callback(ctx, command=command)

    async def send_pages(self, pages):
        """
        Sends embed pages using paginator.
        """
        await menus.UniversalPaginator(pages).start(self.context)

    async def create_cog_page(self, cog: commands.Cog):
        """
        Creates command pages for a given cog.
        """
        _commands = await self.filter_commands(cog.get_commands())

        if not _commands:
            return

        command_page = discord.Embed(
            title=cog.qualified_name.title(),
            description=cog.description,
            colour=discord.Colour.purple(),
        )

        for command in sorted(_commands, key=lambda c: c.name):
            if not command.hidden:
                command_page.add_field(
                    name=command.name, value=command.brief, inline=False
                )

        return command_page

    async def send_bot_help(self, mapping: dict) -> None:
        """
        Overwrites send_bot_help to implement Requiem specific behavior.
        """
        category_page = discord.Embed(
            title="Categories", colour=discord.Colour.purple()
        )
        pages = [category_page]

        for _, cog in self.context.bot.cogs.items():
            if cog_page := await self.create_cog_page(cog):
                category_page.add_field(
                    name=cog.qualified_name.title(), value=cog.description, inline=False
                )
                pages.append(cog_page)

        await self.send_pages(pages)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        """
        Overwrites send_cog_help to implement Requiem specific behavior.
        """
        page = await self.create_cog_page(cog)

        if not page:
            return

        await self.send_pages((page,))

    async def send_command_help(self, command: commands.Command) -> None:
        """
        Overwrites send_command_help to implement requiem specific behavior.
        """
        ctx = self.context

        await command.can_run(ctx)

        embed = discord.Embed(
            title=command.name, description=command.help, colour=discord.Colour.purple()
        )

        parent = command.full_parent_name
        alias = f"{parent} {command.name}" if parent else command.name

        embed.add_field(
            name="Usage",
            value=f"{self.clean_prefix}{alias} {command.signature}",
            inline=False,
        )

        await ctx.send(embed=embed)

    async def send_error_message(self, error: str):
        return
