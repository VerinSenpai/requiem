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


from core import context, client
from discord.ext import commands

import discord


class Developer(commands.Cog, name="developer"):
    """
    Manage client and installed plugins.
    """

    def __init__(self) -> None:
        super().__init__()
        self.last_plugin = None

    @commands.command(brief="View and manage plugins.")
    @commands.is_owner()
    async def plugins(self, ctx: context.Context) -> None:
        """
        Display available plugins and their respective status.
        """
        loaded_plugins = ctx.bot.extensions.keys()
        plugin_states = []

        for plugin in tuple(ctx.bot.all_plugins):
            if plugin == self.last_plugin:
                plugin += " (Most Recent)"

            if plugin in loaded_plugins:
                plugin_states.append(f"{plugin} loaded")
            else:
                plugin_states.append(f"{plugin} not loaded")

        embed = discord.Embed(
            title="Available Plugins",
            description="\n".join(plugin_states),
            colour=ctx.colour,
        )
        await ctx.send(embed=embed)

    @commands.command(brief="Load a given plugin.", aliases=("l",))
    @commands.is_owner()
    async def load(self, ctx: context.Context, plugin: str = None) -> None:
        """
        Load a given plugin.
        """
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.load_extension(plugin)
                self.last_plugin = plugin
                output = "The plugin <%s> has been loaded successfully!" % plugin

            except commands.ExtensionNotFound:
                output = "The plugin <%s> does not exist!" % plugin

            except commands.ExtensionAlreadyLoaded:
                output = "The plugin <%s> is already loaded!" % plugin
        else:
            output = "No plugin was specified!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

    @commands.command(brief="Unload a given plugin.", aliases=("ul",))
    @commands.is_owner()
    async def unload(self, ctx: context.Context, plugin: str = None) -> None:
        """
        Unload a given plugin.
        """
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.unload_extension(plugin)
                self.last_plugin = plugin
                output = "The plugin <%s> has been unloaded successfully!" % plugin

            except commands.ExtensionNotFound:
                output = "The plugin <%s> does not exist!" % plugin

            except commands.ExtensionNotLoaded:
                output = "The plugin <%s> is not loaded!" % plugin
        else:
            output = "No plugin was specified!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

    @commands.command(brief="Reload a given plugin.", aliases=("rl",))
    @commands.is_owner()
    async def reload(self, ctx: context.Context, plugin: str = None) -> None:
        """
        Reload a given plugin.
        """
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.reload_extension(plugin)
                self.last_plugin = plugin
                output = "The plugin <%s> has been reloaded successfully!" % plugin

            except commands.ExtensionNotFound:
                output = "The plugin <%s> does not exist!" % plugin

            except commands.ExtensionNotLoaded:
                output = "The plugin <%s> is not loaded!" % plugin
        else:
            output = "No plugin was specified!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)


def setup(bot: client.Requiem) -> None:
    bot.add_cog(Developer())
