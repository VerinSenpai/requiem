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

from core import models, constants
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

    @commands.group(brief="Manage the greeting channel and message for this guild.", aliases=["greet", "welcome"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2.5)
    async def greeting(self, ctx: commands.Context) -> None:
        """
        View the current greeting configuration for this guild.
        """
        if ctx.invoked_subcommand:
            return

        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        channel = discord.utils.get(ctx.guild.channels, id=guild_config.welcome_channel)
        message = guild_config.welcome_message

        if not message:
            message = "Welcome %user%!"

        for key, value in constants.REPLACEMENTS.items():
            message = message.replace(key, value(ctx.author))

        embed = discord.Embed(title="Guild Greeting Configuration", colour=discord.Colour.purple())
        embed.add_field(name="Channel", value=channel or "Not Configured", inline=False)
        embed.add_field(name="Message", value=message, inline=False)
        await ctx.send(embed=embed)

    @greeting.command(brief="Configure the greeting channel for this guild.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2.5)
    async def channel(self, ctx: commands.Context, channel: discord.TextChannel = None) -> None:
        """
        Configure the greeting channel for this guild.
        """
        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        current_channel = discord.utils.get(ctx.guild.channels, id=guild_config.welcome_channel)

        if not current_channel == channel:
            entry = models.Guilds.filter(snowflake=ctx.guild.id)

            if channel:
                output = f"Alright! The greeting channel has been set to <{channel}>!"
                await entry.update(welcome_channel=channel.id)

            else:
                output = "Alright! The greeting service has been disabled!"
                await entry.update(welcome_channel=0)

        else:
            channel_msg = f"set to <{current_channel}>" if current_channel else "disabled"
            output = f"The greeting channel is already <{channel_msg}>"

        embed = discord.Embed(title="Guild Greeting Configuration", description=output, colour=discord.Colour.purple())
        await ctx.send(embed=embed)

    @greeting.command(brief="Configure the greeting message for this guild.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2.5)
    async def message(self, ctx: commands.Context, message: str = None) -> None:
        """
        Configure the greeting message for this guild.
        """
        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        current_message = guild_config.welcome_message

        if not current_message == message:
            entry = models.Guilds.filter(snowflake=ctx.guild.id)

            if message:
                if len(message) <= 1024:
                    output = "Alright! You have set the greeting message!"
                    await entry.update(welcome_message=message)

                else:
                    output = "The message provided was too large! Please limit your message to 1024 characters!"

            else:
                output = "Alright! The greeting message has been reset!"
                await entry.update(welcome_message="")

        else:
            output = f"The greeting service is already using that message!"

        embed = discord.Embed(title="Guild Greeting Configuration", description=output, colour=discord.Colour.purple())
        await ctx.send(embed=embed)

    @commands.group(brief="Manage the farewell channel and message for this guild.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2.5)
    async def farewell(self, ctx: commands.Context) -> None:
        """
        View the current farewell configuration for this guild.
        """
        if ctx.invoked_subcommand:
            return

        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        channel = discord.utils.get(ctx.guild.channels, id=guild_config.farewell_channel)
        message = guild_config.farewell_message

        if not message:
            message = "Farewell %user%!"

        for key, value in constants.REPLACEMENTS.items():
            message = message.replace(key, value(ctx.author))

        embed = discord.Embed(title="Guild Farewell Configuration", colour=discord.Colour.purple())
        embed.add_field(name="Channel", value=channel or "Not Configured", inline=False)
        embed.add_field(name="Message", value=message, inline=False)
        await ctx.send(embed=embed)

    @farewell.command(name="channel", brief="Configure the farewell channel for this guild.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2.5)
    async def _channel(self, ctx: commands.Context, channel: discord.TextChannel = None) -> None:
        """
        Configure the farewell channel for this guild.
        """
        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        current_channel = discord.utils.get(ctx.guild.channels, id=guild_config.farewell_channel)

        if not current_channel == channel:
            entry = models.Guilds.filter(snowflake=ctx.guild.id)

            if channel:
                output = f"Alright! The farewell channel has been set to <{channel}>!"
                await entry.update(farewell_channel=channel.id)
            else:
                output = "Alright! The farewell service has been disabled!"
                await entry.update(farewell_channel=0)

        else:
            channel_msg = f"set to <{current_channel}>" if current_channel else "disabled"
            output = f"The farewell channel is already <{channel_msg}>"

        embed = discord.Embed(title="Guild Farewell Configuration", description=output, colour=discord.Colour.purple())
        await ctx.send(embed=embed)

    @farewell.command(name="message", brief="Configure the farewell message for this guild.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2.5)
    async def _message(self, ctx: commands.Context, message: str = None) -> None:
        """
        Configure the farewell message for this guild.
        """
        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        current_message = guild_config.farewell_message

        if not current_message == message:
            entry = models.Guilds.filter(snowflake=ctx.guild.id)

            if message:
                if len(message) <= 1024:
                    output = "Alright! You have set the farewell message!"
                    await entry.update(farewell_message=message)

                else:
                    output = "The message provided was too large! Please limit your message to 1024 characters!"

            else:
                output = "Alright! The farewell message has been reset!"
                await entry.update(farewell_message="")

        else:
            output = f"The farewell service is already using that message!"

        embed = discord.Embed(title="Guild Farewell Configuration", description=output, colour=discord.Colour.purple())
        await ctx.send(embed=embed)

    @commands.command(brief="Configure the role for automatic role assignment.")
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 2.5)
    async def autorole(self, ctx: commands.Context, role: discord.Role = None) -> None:
        """
        Configure the role for automatic role assignment.
        """
        guild_config = await models.Guilds.get(snowflake=ctx.guild.id)
        current_role = discord.utils.get(ctx.guild.roles, id=guild_config.auto_role)

        if not current_role == role:
            entry = models.Guilds.filter(snowflake=ctx.guild.id)

            if role:
                output = f"Alright! The ARA has been set to <{role}>!"
                await entry.update(farewell_channel=role.id)
            else:
                output = "Alright! The ARA service has been disabled!"
                await entry.update(farewell_channel=0)

        else:
            channel_msg = f"set to <{current_role}>" if current_role else "disabled"
            output = f"The ARA role is already <{channel_msg}>"

        embed = discord.Embed(title="Auto Role Configuration", description=output, colour=discord.Colour.purple())
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildConfig())
