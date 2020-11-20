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
from core import models

from discord.ext import commands


class GuildConfig(commands.Cog, name="guild config"):
    """
    Various guild specific settings.
    """

    @commands.command(brief="Set the prefix for this guild.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2.5)
    async def prefix(self, ctx: commands.Context, prefix: str = None) -> None:
        """
        Set the prefix for this guild.
        If a prefix is not specified, the default will be restored!
        """
        cache = ctx.bot.cached_configs
        current = await cache.get(ctx.guild.id)
        prefix = prefix or ctx.bot.config.default_prefix

        if prefix == current:
            output = f"The prefix is already set to <{prefix}>!"

        elif len(prefix) <= 5:
            await models.Guilds.filter(snowflake=ctx.guild.id).update(prefix=prefix)
            await cache.set(ctx.guild.id, prefix)
            output = f"Alright! The prefix is now <{prefix}>!"

        else:
            output = "The prefix can be no longer than 5 characters!"

        embed = discord.Embed(description=output, colour=discord.Colour.purple())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildConfig())
