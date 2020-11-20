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


import contextlib
import traceback
import tortoise
import logging
import asyncpg
import discord
import random
import socket
import yarl
import sys
import os
import io

from core import config, constants, help, models
from discord.ext import commands
from aiocache import Cache


_LOGGER = logging.getLogger("requiem.bot")


class Requiem(commands.AutoShardedBot):
    """
    Custom bot class implementing Requiem specific features and handlers.
    """

    def __init__(self, bot_config: config.Config) -> None:
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix=None,
            owner_ids=bot_config.owner_ids,
            help_command=help.HelpCommand(),
            case_insensitive=True,
            intents=intents,
        )

        self.config = bot_config
        self.cached_prefixes = Cache(Cache.MEMORY)
        self.loop.run_until_complete(start_database(bot_config.postgres))

    async def on_ready(self) -> None:
        """
        Implements on_ready event to handle plugin loading.
        """
        if self.extensions:
            return

        _LOGGER.info("requiem has logged in as <%s:%s>!", self.user.name, self.user.id)

        plugins = (
            plugin[:-3]
            for plugin in os.listdir("plugins")
            if plugin not in ("__init__.py", "__pycache__")
        )

        for plugin in plugins:
            try:
                self.load_extension(f"plugins.{plugin}")
                _LOGGER.info("requiem has successfully loaded the plugin <%s>!", plugin)

            except Exception as exc:
                await self.report_error("load_extension", exc)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """
        Implements on_guild_join event to handle guild config  and cache creation on guild join/available.
        """
        saved, created = await models.Guilds.get_or_create(
            defaults={"prefix": self.config.default_prefix}, snowflake=guild.id
        )
        cached = await self.cached_prefixes.get(guild.id)

        if created:
            _LOGGER.info("requiem has created a config entry for guild <%s>!", guild.id)

        if not cached:
            await self.cached_prefixes.add(guild.id, saved.prefix)

    async def on_guild_available(self, guild: discord.Guild) -> None:
        """
        Implements on_guild_available event to handle guild config and cache correction.
        """
        await self.on_guild_join(guild)

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        """
        Overwrites on_error to implement custom event error reporting.
        """
        await self.report_error(event_method, sys.exc_info()[1])

    async def on_command_error(
        self, ctx: commands.Context, exc: commands.CommandError
    ) -> None:
        """
        Overwrites on_command_error to implement custom command error reporting.
        """
        exc_name = exc.__class__.__name__

        if isinstance(exc, commands.CommandNotFound):
            return

        elif isinstance(exc, commands.CommandInvokeError):
            response = random.choice(constants.UNHANDLED)
            await self.report_error(ctx.command.name, exc)

        elif exc_name in constants.HANDLED:
            response = constants.HANDLED.get(exc_name)(ctx, exc)

        else:
            response = str(exc)

        embed = discord.Embed(description=response, colour=discord.Colour.red())
        await ctx.send(embed=embed)

    async def on_command_completion(self, ctx: commands.Context) -> None:
        """
        Implements on_command to handle logging command execution on command.
        """
        _LOGGER.info(
            "user <%s> executed command <%s> in <%s>",
            ctx.author,
            ctx.command,
            ctx.channel,
        )

    async def on_message_edit(
        self, message: discord.Message, message_edit: discord.Message
    ) -> None:
        """
        Implements on_message_edit to handle command execution on message edit.
        """
        await self.process_commands(message_edit)

    async def get_prefix(self, message: discord.Message) -> str:
        """
        Determines current prefix based on context. Also returns prefix if configured to on mention.
        If you're wondering why I do this, so am I so don't ask.
        """
        if message.guild:
            prefix = await self.cached_prefixes.get(message.guild.id)

        else:
            prefix = self.config.default_prefix

        if self.config.prefix_on_mention and self.user.mentioned_in(message):
            response = random.choice(constants.PREFIX)(prefix)
            embed = discord.Embed(description=response, colour=discord.Colour.purple())
            await message.channel.send(embed=embed)

        return prefix

    async def close(self) -> None:
        """
        Overwrites close to properly close database as bot exits.
        """
        await super().close()
        await tortoise.Tortoise.close_connections()

    async def report_error(self, method: str, exc: BaseException) -> None:
        """
        Logs an exceptions occurrence to the database and reports it to the owners if configured to do so.
        """
        if not self.config.report_errors:
            return

        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
        file = discord.File(fp=io.StringIO(tb), filename="error_report.txt")

        for owner_id in self.owner_ids:
            with contextlib.suppress(discord.Forbidden, discord.NotFound):
                owner = self.get_user(owner_id)
                await owner.send(file=file)

        _LOGGER.error(
            f"requiem has encountered an exception while executing method <{method}>! it has been reported!"
        )


async def start_database(cfg: config.PostgresConfig) -> None:
    """
    Starts database connection with postgres server or sqlite.
    """

    async def handle_invalid(value: str) -> None:
        """
        Logs invalid config values and creates sqlite database.
        """
        _LOGGER.warning(
            "requiem was unable to connect to the postgres server because the provided <%s> was invalid! requiem will "
            "use sqlite instead!",
            value,
        )
        await tortoise.Tortoise.init(db_url="sqlite://db.sqlite3", modules=modules)

    url = yarl.URL.build(
        scheme="postgres",
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        path=f"/{cfg.database}",
    )
    modules = {"models": ["core.models"]}

    try:
        await tortoise.Tortoise.init(db_url=str(url), modules=modules)
        _LOGGER.info("requiem has connected to the postgres server at <%s>!", url)

    except (socket.gaierror, ConnectionRefusedError):
        await handle_invalid("host/port")

    except asyncpg.InvalidPasswordError:
        await handle_invalid("user/password")

    except tortoise.exceptions.DBConnectionError:
        await handle_invalid("database")

    await tortoise.Tortoise.generate_schemas()