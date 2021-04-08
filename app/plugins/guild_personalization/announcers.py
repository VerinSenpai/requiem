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
from core import models


replacements = {
    "%user%": lambda member: member.name,
    "%user_mention%": lambda member: member.mention,
    "%guild%": lambda member: member.guild.name,
}


class Announcers:
    """
    Cog for on_member_join and on_member_leave announcers and role assignment.
    """

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Implements on_member_join greeting and automatic role assignment.
        """
        guild_config = await models.Guilds.get(snowflake=member.guild.id)

        role = discord.utils.get(member.guild.roles, id=guild_config.auto_role)
        channel = discord.utils.get(
            member.guild.channels, id=guild_config.welcome_channel
        )
        message = guild_config.welcome_message

        if role:
            await member.add_roles((role,), reason="Automatic Role Assignment")

        if not channel:
            return

        if not message:
            message = "Welcome %user%!"

        for key, value in REPLACEMENTS.items():
            message = message.replace(key, value(member))

        embed = discord.Embed(colour=discord.Colour.purple(), description=message)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """
        Implements on_member_leave farewell announcer.
        """
        guild_config = await models.Guilds.get(snowflake=member.guild.id)
        channel = discord.utils.get(
            member.guild.channels, id=guild_config.farewell_channel
        )
        message = guild_config.farewell_message

        if not channel:
            return

        if not message:
            message = "Farewell %user%!"

        for key, value in REPLACEMENTS.items():
            message = message.replace(key, value(member))

        embed = discord.Embed(colour=discord.Colour.purple(), description=message)
        await channel.send(embed=embed)


def setup(bot: Requiem) -> None:
    bot.add_cog(Announcers())
