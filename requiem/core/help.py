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
import typing


class HelpCommand(commands.HelpCommand):
    """
    Custom embedded HelpCommand.
    """

    async def send_pages(self, pages: typing.List[discord.Embed]) -> None:
        """
        Sends prepared pages.
        """
        paginator = menus.Paginator(pages)
        await paginator.start(self.context)

    async def send_bot_help(self, mapping: typing.Dict[commands.Cog, typing.List[commands.Command]]) -> None:
        """
        Generates pages containing cogs with available commands.
        """
        cog_pages = []
        cog_page = discord.Embed(colour=self.context.colour)

        for cog, _commands in mapping.items():
            if not cog:
                continue

            filtered = await self.filter_commands(_commands)

            if not filtered:
                continue

            if len(cog_page.fields) > 10:
                cog_pages.append(cog_page)
                cog_page = discord.Embed(colour=self.context.colour)

            cog_page.add_field(
                name=cog.qualified_name.title(),
                value=cog.description,
                inline=False
            )

        if cog_page not in cog_pages:
            cog_pages.append(cog_page)

        await self.send_pages(cog_pages)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        """
        Generates pages containing commands for a specified cog.
        """
        def create_page() -> discord.Embed:
            return discord.Embed(
                title=cog.qualified_name.title(),
                description=cog.description,
                colour=self.context.colour
            )

        _commands = cog.get_commands()
        filtered = await self.filter_commands(_commands, sort=True)

        if not filtered:
            return

        command_pages = []
        command_page = create_page()

        for command in filtered:
            if len(command_page.fields) > 10:
                command_pages.append(command_page)
                command_page = create_page()

            command_page.add_field(
                name=command.name,
                value=command.brief,
                inline=False
            )

        if command_page not in command_pages:
            command_pages.append(command_page)

        await self.send_pages(command_pages)

    async def send_group_help(self, group: commands.Group) -> None:
        """
        Generates pages containing commands for a specified group.
        """
        filtered = await self.filter_commands(group.commands, sort=True)

        if not filtered:
            return

        group_pages = []
        group_page = discord.Embed(colour=self.context.colour)

        group_page.add_field(name=group.name, value=group.help)

        for command in filtered:
            if len(group_page.fields) > 10:
                group_pages.append(group_page)
                group_page = discord.Embed(colour=self.context.colour)

            group_page.add_field(
                name=command.name,
                value=command.brief,
                inline=False
            )

        if group_page not in group_pages:
            group_pages.append(group_page)

        await self.send_pages(group_pages)

    async def send_command_help(self, command: commands.Command) -> None:
        """
        Sends command help.
        """
        usage = self.get_command_signature(command)
        embed = discord.Embed(
            title=command.name,
            description=command.help,
            colour=self.context.colour
        )
        embed.set_footer(text=usage)
        await self.context.send(embed=embed)

    def command_not_found(self, string: str) -> str:
        """
        Returns command_not_found string.
        """
        return f"No command or cog called **{string}** exists!"

    async def send_error_message(self, error: str) -> None:
        """
        Sends an error message.
        """
        embed = discord.Embed(description=error, colour=self.context.colour)
        await self.context.send(embed=embed)
