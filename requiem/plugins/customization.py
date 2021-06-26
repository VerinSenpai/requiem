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


from core import context, client, constants, models
from discord.ext import commands

import discord


class Customization(commands.Cog, name="customization"):
    """
    Customize how you interact with Requiem on this guild.
    """

    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.command(brief="Change the command prefix.")
    async def prefix(self, ctx: context.Context, prefix: str = None) -> None:
        """
        Set the command prefix for this guild.
        """
        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        prefix = prefix or ctx.bot.command_prefix

        if guild_config.prefix == prefix:
            output = f"The prefix is already set to <{prefix}>!"

        elif len(prefix) > 4:
            output = "Please limit  the length of your prefix to 4 or less characters!"

        else:
            output = f"Alright! The prefix is set to <{prefix}>!"
            guild_config.prefix = prefix
            await guild_config.save()
            await ctx.bot.cache.set(ctx.guild.id, guild_config)

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.command(brief="Change the embed colour.")
    async def colour(self, ctx: context.Context, colour: str = None) -> None:
        """
        Set the embed colour for this guild.
        """
        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        colour = colour or "purple"
        available_colours = constants.colours.keys()

        if guild_config.colour == colour:
            output = f"The embed colour is already set to <{colour}>!"

        elif colour not in available_colours:
            available_colours_string = "\n".join(available_colours)
            output = (
                f"Please specify a valid embed colour!\n"
                f"The following colours are available:\n"
                f"{available_colours_string}"
            )

        else:
            output = (
                f"Alright! The embed colour is set to <{colour}>!\n"
                f"The change will take affect in the next embed!"
            )
            guild_config.colour = colour
            await guild_config.save()
            await ctx.bot.cache.set(ctx.guild.id, guild_config)

        embed = discord.Embed(description=output, colour=ctx.colour)
        await ctx.send(embed=embed)


def setup(bot: client.Requiem) -> None:
    bot.add_cog(Customization())
