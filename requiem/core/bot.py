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
import aiocache

from core import config, models, constants, help
from discord.ext.commands import view
from discord.ext import commands

import contextlib
import traceback
import aiocache
import tortoise
import logging
import discord
import typing
import random
import sys
import os
import io


LOGGER = logging.getLogger("requiem.client")


class Context(commands.Context):
    """
    Subclass of commands.Context implementing Requiem specific methods and attributes.
    """

    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.colour = attrs.pop("colour")


class Requiem(commands.AutoShardedBot):
    """
    Custom Requiem client based on <discord.ext.commands.AutoShardedBot>.
    """

    def __init__(self, credentials: config.Credentials) -> None:
        """
        Sets up required intents.
        """

        intents = discord.Intents.all()
        intents.members = True

        super().__init__(
            command_prefix=credentials.default_prefix,
            intents=intents,
            owner_ids=credentials.owner_ids,
            help_command=help.HelpCommand(),
        )

        self.credentials = credentials
        self.cache = aiocache.SimpleMemoryCache()

    @property
    def all_plugins(self) -> typing.Generator[str, any, None]:
        """
        Returns generator of plugin names from plugins folder.
        """
        return (
            f"plugins." + plugin.replace(".py", "")
            for plugin in os.listdir("plugins")
            if plugin not in ("__init__.py", "__pycache__")
        )

    def load_extension(self, name: str, *, package=None):
        """
        Adds logging to extension loading.
        """
        super().load_extension(name, package=package)
        LOGGER.info("plugin <%s> loaded!", name)

    def unload_extension(self, name: str, *, package=None) -> None:
        """
        Adds logging to extension unloading.
        """
        super().unload_extension(name, package=package)
        LOGGER.info("plugin <%s> unloaded!", name)

    async def start(self, *args, **kwargs) -> None:
        """
        Inserts plugin loading into start coroutine.
        """
        for plugin in self.all_plugins:
            try:
                self.load_extension(plugin)

            except Exception as exc:
                await self.report_error(exc)

        await super().start(*args, **kwargs)

    async def close(self) -> None:
        """
        Shuts the bot down and closes connection to tortoise.
        """
        LOGGER.info("requiem is shutting down!")
        await super().close()
        await tortoise.Tortoise.close_connections()

    async def report_error(self, exc: Exception) -> None:
        """
        Reports error occurrences to owners and console.
        """
        LOGGER.error("requiem has encountered an exception!", exc_info=exc)

        if not self.credentials.report_errors:
            return

        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
        string_io = io.StringIO("".join(tb))
        file = discord.File(fp=string_io, filename="error_report.txt")

        for owner_id in self.owner_ids:
            owner = self.get_user(owner_id)

            if not owner:
                continue

            with contextlib.suppress(discord.Forbidden, discord.NotFound):
                await owner.send(file=file)

    async def on_command_error(self, ctx, exc: Exception) -> None:
        """
        Catches and reports or handles unhandled command exceptions.
        """
        exc_name = exc.__class__.__name__

        if isinstance(exc, commands.CommandNotFound):
            return

        elif isinstance(exc, commands.CheckFailure):
            return

        elif isinstance(exc, commands.CommandInvokeError):
            await self.report_error(exc)
            response = random.choice(constants.unhandled_errors)

        elif exc_name in constants.handled_errors:
            response = constants.handled_errors.get(exc_name)(ctx, exc)

        else:
            return

        embed = discord.Embed(description=response, colour=discord.Colour.red())
        await ctx.send(embed=embed)

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        """
        Catches and reports unhandled exceptions raised by event methods.
        """
        _, exc, _ = sys.exc_info()
        await self.report_error(exc)

    async def on_ready(self) -> None:
        """
        Logs ready state to console.
        """
        LOGGER.info("requiem is logged in as <%s:%s>!", self.user.name, self.user.id)

    async def on_message(self, message: discord.Message) -> None:
        """
        Responds to prefix requests or calls process commands.
        """
        if not message.content == f"<@!{self.user.id}>":
            await self.process_commands(message)

        elif self.credentials.prefix_on_mention:
            ctx = await self.get_context(message)
            response = random.choice(constants.prefix_responses)(f"**{ctx.prefix}**")
            embed = discord.Embed(description=response, colour=ctx.colour)
            await ctx.send(embed=embed)

    async def on_message_edit(
        self, message: discord.Message, message_edit: discord.Message
    ) -> None:
        """
        Forwards on_message_edit to on_message.
        """
        await self.on_message(message_edit)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """
        Handles guild config creation on guild join.
        """
        saved, created = await models.Guilds.get_or_create(
            defaults={"prefix": self.credentials.default_prefix}, snowflake=guild.id
        )

        if created:
            LOGGER.info("requiem has created a config entry for guild <%s>!", guild.id)

    async def on_guild_available(self, guild: discord.Guild) -> None:
        """
        Handles guild config creation for missed guilds on bot start.
        """
        await self.on_guild_join(guild)

    async def set_prefix_and_colour(self, guild_config: models.Guilds) -> None:
        """
        Updates guild prefix and colour in cache.
        """
        values = (guild_config.prefix, guild_config.colour)
        await self.cache.set(guild_config.snowflake, values)

    async def get_prefix_and_colour(self, message: discord.Message) -> typing.Tuple[str, str]:
        """
        Retrieve prefix and colour based on context from defaults, database, or cache.
        """
        if not message.guild:
            return self.command_prefix, "purple"

        cached = await self.cache.get(message.guild.id)
        if cached:
            return cached

        guild_config = await models.Guilds.get(snowflake=message.guild.id)
        await self.set_prefix_and_colour(guild_config)
        return guild_config.prefix, guild_config.colour

    async def get_context(self, message: discord.Message, *, cls=Context) -> Context:
        """
        Overwrites default get_context coroutine removing unnecessary checks and adding colour to the context.
        """
        string_view = view.StringView(message.content)
        prefix, colour = await self.get_prefix_and_colour(message)
        colour = constants.colours.get(colour)()
        string_view.skip_string(prefix)
        invoker = string_view.get_word()
        command = self.all_commands.get(invoker)
        ctx = cls(
            prefix=prefix,
            colour=colour,
            invoker=invoker,
            command=command,
            view=string_view,
            bot=self,
            message=message
        )
        return ctx
