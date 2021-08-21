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
    Owner only commands for managing and testing Requiem.
    """

    def __init__(self):
        super().__init__()
        self.last_extension = None

    @commands.command(brief="Attempts to load a given extension.", aliases=("l",))
    @commands.is_owner()
    async def load(self, ctx: bot.Context, extension: str = None) -> None:
        """
        Attempts to load a specified extension.

        If no extension is specified, will attempt to load the last specified plugin.
        """
        exc = None
        extension = extension or self.last_extension

        if extension:
            try:
                ctx.bot.load_extension(extension)
                output = f"The extension <{extension}> has been loaded successfully!"

            except commands.ExtensionAlreadyLoaded:
                output = f"The extension <{extension}> is already loaded!"

            except commands.ExtensionNotFound:
                output = f"The extension <{extension}> could not be found!"

            except Exception as exc:
                output = f"The extension <{extension}> failed to load because of an error!"
                exc = exc

        else:
            output = "You did not specify an extension to be loaded!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

        if exc:
            raise exc

    @commands.command(brief="Attempts to unload a given extension.", aliases=("ul",))
    @commands.is_owner()
    async def unload(self, ctx: bot.Context, extension: str = None) -> None:
        """
        Attempts to unload a specified extension.

        If no extension is specified, will attempt to unload the last specified plugin.
        """
        exc = None
        extension = extension or self.last_extension

        if extension:
            try:
                ctx.bot.unload_extension(extension)
                output = f"The extension <{extension}> has been unloaded successfully!"

            except commands.ExtensionNotLoaded:
                output = f"The extension <{extension}> is not loaded!"

            except Exception as exc:
                output = f"The extension <{extension}> failed to unload because of an error!"
                exc = exc

        else:
            output = "You did not specify an extension to be loaded!"

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

        if exc:
            raise exc


def setup(requiem: bot.Requiem) -> None:
    """
    Attaches Owner cog to Requiem.
    """
    requiem.add_cog(Owner())
