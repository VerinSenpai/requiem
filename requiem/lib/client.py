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


from lib import tasks, models

import lightbulb
import tortoise
import logging
import random
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

    def __init__(self, credentials: models.Credentials) -> None:
        super().__init__(
            token=credentials.token,
            banner=None,
            default_enabled_guilds=credentials.enabled_guilds,
        )

        self.credentials = credentials
        self.executed_commands = 0

        self.subscribe(hikari.StartingEvent, self.handle_starting_operations)
        self.subscribe(hikari.StartedEvent, self.handle_started_operations)
        self.subscribe(hikari.StoppingEvent, self.handle_stopping_operations)
        self.subscribe(lightbulb.SlashCommandCompletionEvent, self.handle_command_completion)

    async def handle_starting_operations(self, _) -> None:
        """
        Prepares the database and loads extensions.
        """
        await setup_database(self.credentials)

        extensions = (
            plugin
            for plugin in os.listdir("extensions")
            if plugin not in ("__init__.py", "__pycache__")
        )

        for extension in extensions:
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

    async def handle_started_operations(self, _) -> None:
        """
        Starts any post-start tasks
        """
        handle_presence.start(self)

    async def handle_stopping_operations(self, _) -> None:
        """
        Unloads extensions and closes the database while Requiem is closing.
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

        await tortoise.Tortoise.close_connections()

        _LOGGER.info("requiem has finished cleanup!")

    async def handle_command_completion(self, event: lightbulb.SlashCommandCompletionEvent) -> None:
        self.executed_commands += 1

        _LOGGER.info("command %s executed successfully!", event.command.name)


async def setup_database(credentials: models.Credentials) -> None:
    """
    Attempts a connection to a postgresql server. Falls back to using sqlite.
    """
    url = yarl.URL.build(
        scheme="postgres",
        host=credentials.postgres_host,
        port=credentials.postgres_port,
        user=credentials.postgres_user,
        password=credentials.postgres_password,
        path=f"/{credentials.postgres_database}",
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


@tasks.loop(minutes=5)
async def handle_presence(bot: Requiem) -> None:
    possible = (
        "Listening for Slash Commands",
        "Waiting for something to do",
        "Grinding gears"
    )
    activity = hikari.Activity(name=random.choice(possible))
    await bot.update_presence(activity=activity)
