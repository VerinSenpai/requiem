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
import time

from discord.ext import commands
from core.bot import Requiem
from discord import Colour


class Utility(commands.Cog, name="utility"):
    """
    Various utility and informational commands.
    """

    @commands.command(brief="View information about a given users account.")
    @commands.cooldown(1, 2.5)
    async def user(
        self, ctx: commands.Context, *, user: discord.Member or discord.User = None
    ) -> None:
        """
        View information about a given users account.
        """
        user = user or ctx.author
        embed = discord.Embed(colour=Colour.purple())
        embed.add_field(name="Username", value=user.name)
        embed.add_field(name="Display Name:", value=user.display_name)

        embed.add_field(name="Snowflake:", value=user.id)
        embed.add_field(
            name="Account Created On:",
            value=f'{user.created_at.strftime("%A %B %d, %Y")}',
        )

        if ctx.guild:
            embed.add_field(
                name="Member Joined On:",
                value=f'{user.joined_at.strftime("%A %B %d, %Y")}',
            )
            roles = (
                " ".join(role.mention for role in user.roles[1:])
                or "This user has no roles!"
            )
            embed.add_field(name="Roles", value=roles, inline=False)

        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief="View information about this guild.", aliases=("server",))
    @commands.cooldown(1, 2.5)
    @commands.guild_only()
    async def guild(self, ctx: commands.Context) -> None:
        """
        View information about this guild.
        """
        embed = discord.Embed(color=Colour.purple())
        embed.add_field(name="Name", value=ctx.guild.name)
        embed.add_field(name="Snowflake", value=ctx.guild.id)
        embed.add_field(name="Region", value=ctx.guild.region)
        embed.add_field(
            name="Guild Verification Level", value=ctx.guild.verification_level
        )
        embed.add_field(
            name="Guild Created On", value=ctx.guild.created_at.strftime("%A %B %d, %Y")
        )
        embed.add_field(name="Members", value=ctx.guild.member_count)
        embed.add_field(name="Roles", value=f"{len(ctx.guild.roles)}")
        embed.add_field(name="Text Channels", value=f"{len(ctx.guild.channels)}")
        embed.add_field(name="Voice Channels", value=f"{len(ctx.guild.voice_channels)}")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Test heartbeat and ACK latency.")
    @commands.cooldown(1, 2.5)
    async def ping(self, ctx: commands.Context) -> None:
        """
        Test heartbeat and ACK latency.
        """
        embed = discord.Embed(description="Pinging...", color=Colour.purple())
        start = time.monotonic()
        message = await ctx.send(embed=embed)
        millis = (time.monotonic() - start) * 1000
        heartbeat = ctx.bot.latency * 1000
        colour = (
            Colour.red()
            if heartbeat >= 140
            else Colour.gold()
            if heartbeat > 70 < 140
            else Colour.green()
        )
        embed = discord.Embed(colour=colour)
        embed.add_field(name="Heartbeat", value=f"{int(heartbeat)}ms")
        embed.add_field(name="ACK", value=f"{int(millis)}ms")
        await message.edit(embed=embed)

    @commands.command(brief="View a given users avatar.")
    @commands.cooldown(1, 2.5)
    async def avatar(
        self, ctx: commands.Context, *, user: discord.Member or discord.User = None
    ):
        """
        View a given users avatar.
        """
        user = user or ctx.author
        embed = discord.Embed(color=Colour.purple())
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot: Requiem):
    bot.add_cog(Utility())
