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


import random
import discord

from discord.ext import commands


class DevTools(commands.Cog, name="dev tools"):
    """
    Development and testing commands.
    """

    def __init__(self):
        self.last_plugin = None

    @commands.command(brief="Raises a random command error.")
    @commands.is_owner()
    async def error(self, ctx: commands.Context, command_error: bool = False) -> None:
        """
        Raises a random command error. Useful for testing command exception handler.
        """
        command_errors = (
            commands.CommandOnCooldown(
                commands.Cooldown(1, 2.5, commands.BucketType.user), 1.5
            ),
            commands.NotOwner(),
            commands.BotMissingPermissions(("manage_guild", "manage_roles")),
            commands.DisabledCommand(),
            commands.MissingPermissions(("manage_guild", "manage_roles")),
            commands.NoPrivateMessage(),
            commands.NSFWChannelRequired(ctx.channel),
        )

        exception = (
            random.choice(command_errors) if command_error else Exception("HELLO WORLD")
        )

        embed = discord.Embed(
            description=f"Raising {exception.__class__}...",
            colour=discord.Colour.blue(),
        )
        await ctx.send(embed=embed)

        raise exception

    @commands.command(brief="Unloads a given plugin.")
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, plugin: str = None) -> None:
        """
        Attempts to unload a given plugin.
        """
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.unload_extension(f"plugins.{plugin}")
                self.last_plugin = plugin
                output = f"Requiem has successfully unloaded the plugin {plugin}!"

            except commands.errors.ExtensionNotLoaded:
                output = f"Requiem could not unload the plugin {plugin} because it is not loaded!"

            except Exception as exc:
                output = f"Requiem could not unload the plugin {plugin} because an error was encountered!"
                await ctx.bot.report_error("unload_extension", exc)

        else:
            output = "You did not specify a plugin to be loaded!"

        embed = discord.Embed(description=output, colour=discord.Colour.blue())
        await ctx.send(embed=embed)

    @commands.command(brief="Loads a given plugin.")
    @commands.is_owner()
    async def load(self, ctx: commands.Context, plugin: str = None) -> None:
        """
        Attempts to load a given plugin.
        """
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.load_extension(f"plugins.{plugin}")
                self.last_plugin = plugin
                output = f"Requiem has successfully loaded the plugin {plugin}!"

            except commands.errors.ExtensionAlreadyLoaded:
                output = f"Requiem could not load the plugin {plugin} because it is already loaded!"

            except Exception as exc:
                output = f"Requiem could not load the plugin {plugin} because an error was encountered!"
                await ctx.bot.report_error("load_extension", exc)

        else:
            output = "You did not specify a plugin to be loaded!"

        embed = discord.Embed(description=output, colour=discord.Colour.blue())
        await ctx.send(embed=embed)

    @commands.command(brief="Reloads a given plugin.", aliases=("rl",))
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, plugin: str = None) -> None:
        """
        Attempts to reload a given plugin.
        """
        plugin = plugin or self.last_plugin

        if plugin:
            try:
                ctx.bot.reload_extension(f"plugins.{plugin}")
                self.last_plugin = plugin
                output = f"Requiem has successfully reloaded the plugin {plugin}!"

            except commands.errors.ExtensionNotLoaded:
                output = f"Requiem could not reload the plugin {plugin} because it is not loaded!"

            except Exception as exc:
                output = f"Requiem could not reload the plugin {plugin} because an error was encountered!"
                await ctx.bot.report_error("reload_extension", exc)

        else:
            output = "You did not specify a plugin to be reloaded!"

        embed = discord.Embed(description=output, colour=discord.Colour.blue())
        await ctx.send(embed=embed)


def setup(bot: commands.AutoShardedBot) -> None:
    """
    Setup function required by dpy. Adds DevTools as a cog.
    """
    bot.add_cog(DevTools())
