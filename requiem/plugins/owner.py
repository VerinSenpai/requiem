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
from core import bot

import discord


class Owner(commands.Cog, name="owner"):
    """
    Restricted owner only commands that allow for easy management of Requiem.
    """

    def __init__(self) -> None:
        super().__init__()
        self.last_plugin = None

    @commands.command(brief="Load a given plugin.")
    @commands.is_owner()
    async def load(self, ctx: bot.Context, plugin: str = None) -> None:
        """
        Attempt to load a specified plugin.

        If no plugin is specified, will attempt to load the last specified plugin.
        """
        exc = None
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.load_extension(plugin)
                output = f"The plugin <{plugin}> has been loaded successfully!"
                self.last_plugin = plugin

            except commands.ExtensionAlreadyLoaded:
                output = f"The plugin <{plugin}> is already loaded!"

            except commands.ExtensionNotFound:
                output = f"The plugin <{plugin}> could not be found!"

            except Exception as exc:
                output = f"The plugin <{plugin}> could not be loaded because an error has been raised!"
                exc = exc

        else:
            output = f"You must specify a plugin to be loaded!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

        if exc:
            raise exc

    @commands.command(brief="Unload a given plugin.")
    @commands.is_owner()
    async def unload(self, ctx: bot.Context, plugin: str = None) -> None:
        """
        Attempt to unload a specified plugin.

        If no plugin is specified, will attempt to unload the last specified plugin.
        """
        exc = None
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.unload_extension(plugin)
                output = f"The plugin <{plugin}> has been unloaded successfully!"
                self.last_plugin = plugin

            except commands.ExtensionNotLoaded:
                output = f"The plugin <{plugin}> is not loaded!"

            except Exception as exc:
                output = f"The plugin <{plugin}> could not be unloaded because an error has been raised!"
                exc = exc

        else:
            output = f"You must specify a plugin to be unloaded!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

        if exc:
            raise exc

    @commands.command(brief="Reload a given plugin.")
    @commands.is_owner()
    async def load(self, ctx: bot.Context, plugin: str = None) -> None:
        """
        Attempt to reload a specified plugin.

        If no plugin is specified, will attempt to reload the last specified plugin.
        """
        exc = None
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.load_extension(plugin)
                output = f"The plugin <{plugin}> has been reloaded successfully!"
                self.last_plugin = plugin

            except commands.ExtensionNotLoaded:
                output = f"The plugin <{plugin}> is not loaded!"

            except Exception as exc:
                output = f"The plugin <{plugin}> could not be reloaded because an error has been raised!"
                exc = exc

        else:
            output = f"You must specify a plugin to be reloaded!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

        if exc:
            raise exc


def setup(requiem: bot.Requiem) -> None:
    """
    Required setup method used to attach Owner cog to Requiem.
    """
    requiem.add_cog(Owner())
