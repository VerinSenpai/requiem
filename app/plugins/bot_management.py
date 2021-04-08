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


import discord

from discord.ext import commands
from core.bot import Requiem
from discord import Colour


class BotManagement(commands.Cog, name="bot management"):
    """
    Bot extension and command management commands. These commands can only be executed by owners.
    """
    def __init__(self) -> None:
        self.last_plugin = None

    @commands.is_owner()
    @commands.command(brief="Loads a given plugin.")
    async def load(self, ctx: commands.Context, *, name: str = None) -> None:
        """
        Attempts to load a given plugin.
        """
        name = name.replace(" ", "_") or self.last_plugin

        try:
            ctx.bot.load_extension(f"plugins.{name}")
            output = "Requiem has successfully loaded <%s>!", name

        except commands.ExtensionAlreadyLoaded:
            output = f"Requiem could not load <{name}> because it is already loaded!"

        embed = discord.Embed(description=output, colour=Colour.purple())
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(brief="Loads a given plugin.")
    async def unload(self, ctx: commands.Context, *, name: str = None) -> None:
        """
        Attempts to unload a given plugin.
        """
        name = name.replace(" ", "_") or self.last_plugin

        try:
            ctx.bot.unload_extension(f"plugins.{name}")
            output = "Requiem has successfully unloaded <%s>!", name

        except commands.ExtensionNotLoaded:
            output = f"Requiem could not unload <{name}> because it is not loaded!"

        embed = discord.Embed(description=output, colour=Colour.purple())
        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(brief="Loads a given plugin.")
    async def reload(self, ctx: commands.Context, *, name: str = None) -> None:
        """
        Attempts to reload a given plugin.
        """
        name = name.replace(" ", "_") or self.last_plugin

        try:
            ctx.bot.reload_extension(f"plugins.{name}")
            output = f"Requiem has successfully reloaded <{name}>!"

        except commands.ExtensionNotLoaded:
            output = "Requiem could not reload <%s> because it is not loaded!", name

        embed = discord.Embed(description=output, colour=Colour.purple())
        await ctx.send(embed=embed)


def setup(bot: Requiem) -> None:
    bot.add_cog(BotManagement())
