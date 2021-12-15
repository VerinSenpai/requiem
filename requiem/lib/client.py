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


from lib.models import Credentials

import lightbulb
import tortoise
import logging
import asyncpg
import socket
import typing
import hikari
import yarl
import abc
import os


_LOGGER = logging.getLogger("requiem.client")


class Requiem(lightbulb.BotApp, abc.ABC):
    """
    Custom Requiem client based on lightbulb.BotApp that overwrites and implements Requiem specific methods.
    """

    def __init__(self, credentials: Credentials) -> None:
        super().__init__(
            token=credentials.token,
            banner=None,
            default_enabled_guilds=credentials.enabled_guilds,
        )

        self.credentials = credentials

        self.subscribe(hikari.StartingEvent, self.setup_database)
        self.subscribe(hikari.StartingEvent, self.load_extensions_on_start)
        self.subscribe(hikari.StoppingEvent, self.clean_up_on_closing)
        self.subscribe(lightbulb.SlashCommandCompletionEvent, self.log_successful_command_invoke)

    @property
    def all_extensions(self) -> typing.Generator[str, any, None]:
        """
        Returns generator of extension names from extensions folder.
        """
        return (
            plugin
            for plugin in os.listdir("extensions")
            if plugin not in ("__init__.py", "__pycache__")
        )

    async def setup_database(self, event: hikari.StartingEvent) -> None:
        """
        Attempts a connection to a postgresql server. Falls back to using sqlite.
        """
        url = yarl.URL.build(
            scheme="postgres",
            host=self.credentials.postgres_host,
            port=self.credentials.postgres_port,
            user=self.credentials.postgres_user,
            password=self.credentials.postgres_password,
            path=f"/{self.credentials.postgres_database}",
        )
        modules = {"models": ["lib.models"]}

        try:
            await tortoise.Tortoise.init(db_url=str(url), modules=modules)
            _LOGGER.info("requiem has connected to the postgres server at <%s>!", url)

        except (
                tortoise.exceptions.DBConnectionError,
                asyncpg.InvalidPasswordError,
                ConnectionRefusedError,
                socket.gaierror,
        ):
            await tortoise.Tortoise.init(db_url="sqlite://db.sqlite3", modules=modules)
            _LOGGER.warning(
                "requiem was unable to connect to a postgres server! sqlite will be used instead!"
            )

        await tortoise.Tortoise.generate_schemas()

    async def load_extensions_on_start(self, event: hikari.StartingEvent) -> None:
        """
        Loads extensions prior to Requiem connecting to discord.
        Logs number of extensions loaded and number of commands gathered.
        """

        for extension in self.all_extensions:
            try:
                self.load_extensions(f"extensions.{extension}")

            except Exception as exc:
                _LOGGER.error(
                    f"encountered an exception while attempting to load {extension}!",
                    exc_info=exc,
                )

        _LOGGER.info(
            f"successfully loaded {len(self.extensions)} extension(s) and {len(self.slash_commands)} command(s)!"
        )

    async def clean_up_on_closing(self, event: hikari.StoppingEvent) -> None:
        """
        Handles extension unloading and cleanup while Requiem is closing.
        """
        _LOGGER.info("requiem is cleaning up!")

        for extension in self.extensions[::]:
            try:
                self.unload_extensions(extension)

            except Exception as exc:
                _LOGGER.error(
                    f"encountered an exception while attempting to unload {extension}!",
                    exc_info=exc,
                )

        _LOGGER.info("successfully unloaded all extensions and commands!")

        await tortoise.Tortoise.close_connections()

        _LOGGER.info("requiem has finished cleanup!")

    async def log_successful_command_invoke(self, event: lightbulb.SlashCommandCompletionEvent) -> None:
        """
        Adds successful command execution logging to console.
        """
        _LOGGER.info(f"successfully executed command {event.command.name} in guild {event.context.guild_id}!")
