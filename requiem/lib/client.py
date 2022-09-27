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


from cattr import global_converter
from hikari.internal import ux
from requiem.lib import models

import shutil
import logging
import typing
import yaml
import aiohttp
import click
import hikari
import pathlib
import lightbulb
import abc
import datetime
import aerich
import tortoise
import asyncpg
import socket
import os


_LOGGER = logging.getLogger("requiem.client")
T = typing.TypeVar("T")
DATA_DIR = pathlib.Path(click.get_app_dir("requiem"))


def start_failsafe(debug: bool) -> None:
    """
    Attempts to fetch credentials and start Requiem. Ensures any errors get logged before closing.
    """
    flavor = "DEBUG" if debug else "INFO"
    ux.init_logging(flavor, True, True)

    try:
        _LOGGER.info("requiem is fetching the configuration!")

        with open(DATA_DIR / "config.yaml") as stream:
            data = yaml.safe_load(stream)

        credentials = global_converter.structure(data, models.Config)

        _LOGGER.info("requiem has successfully fetched the configuration!")

        requiem = Requiem(credentials)
        requiem.run()

    except FileNotFoundError:
        _LOGGER.warning("requiem was unable to find the configuration! run `requiem setup` to create it!")

    except (KeyError, TypeError, ValueError):
        _LOGGER.warning("requiem was unable to read the configuration! run `requiem setup` to recreate it!")

    except hikari.errors.GatewayServerClosedConnectionError:
        _LOGGER.warning(
            "requiem has closed because the gateway server has closed the connection!"
        )

    except aiohttp.ClientConnectionError:
        _LOGGER.error(
            "requiem was unable to connect to discord! check your internet connection and try again!"
        )

    except hikari.errors.UnauthorizedError:
        _LOGGER.error(
            "requiem was unable to login because the provided token is invalid!"
        )

    except Exception as exc:
        _LOGGER.critical(
            "requiem has encountered a critical exception and crashed!", exc_info=exc
        )


async def _setup_database(url: str) -> None:
    """
    Attempts a connection to a postgresql server. Falls back to using sqlite.
    """
    mig_dir = pathlib.Path(DATA_DIR / "migrations")

    try:
        command = aerich.Command(
            tortoise_config={
                "connections": {
                    "default": url
                },
                "apps": {
                    "models": {
                        "models": [
                            "aerich.models",
                            "requiem.lib.models"
                        ],
                        "default_connection": "default",
                    },
                }
            },
            location=str(DATA_DIR / "migrations")
        )

        if mig_dir.exists():
            await command.init()

            try:
                update = await command.migrate()

                if update:
                    await command.upgrade()
                    _LOGGER.info(f"requiem has updated the database tables!")

            except AttributeError:
                _LOGGER.warning(
                    "requiem was unable to retrieve model history from the database! "
                    "model history will be created from scratch!"
                )

                shutil.rmtree(mig_dir)

                await command.init_db(True)

        else:
            await command.init_db(True)

        _LOGGER.info("requiem has connected to the postgres server at <%s>!", url)

        await tortoise.Tortoise.generate_schemas()

    except (
            tortoise.exceptions.DBConnectionError,
            asyncpg.InvalidPasswordError,
            ConnectionRefusedError,
            socket.gaierror,
    ):
        _LOGGER.warning("requiem was unable to connect to a postgres server!")


class Requiem(lightbulb.BotApp, abc.ABC):
    """
    Custom Requiem client based on lightbulb.BotApp that overwrites and implements Requiem specific methods.
    """

    def __init__(self, config: models.Config) -> None:
        super().__init__(
            token=config.discord_token,
            banner=None,
            default_enabled_guilds=config.enabled_guilds,
        )

        self._config = config
        self._cmds_run = 0
        self._started_at = datetime.datetime.now()

        self.subscribe(hikari.StartingEvent, self._handle_starting_operations)
        self.subscribe(hikari.StoppingEvent, self._handle_stopping_operations)
        self.subscribe(lightbulb.SlashCommandCompletionEvent, self._handle_command_completion)

    @property
    def config(self) -> models.Config:
        return self._config

    @property
    def cmds_run(self) -> int:
        return self._cmds_run

    @property
    def uptime(self) -> datetime.timedelta:
        return datetime.datetime.now() - self._started_at

    async def _handle_starting_operations(self, _: hikari.StartingEvent) -> None:
        """
        Attempts to find and load all extensions.
        """
        await _setup_database(self.config.database_url)

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

    async def _handle_stopping_operations(self, _: hikari.StoppingEvent) -> None:
        """
        Attempts to unload all loaded extensions and close database connections.
        """
        for extension in self.extensions[::]:
            try:
                self.unload_extensions(extension)

            except Exception as exc:
                _LOGGER.error(
                    f"encountered an exception while attempting to unload {extension}!",
                    exc_info=exc,
                )

        await tortoise.Tortoise.close_connections()

    async def _handle_command_completion(self, event: lightbulb.SlashCommandCompletionEvent) -> None:
        """
        Increments cmds_run and logs successful command execution.
        """
        self._cmds_run += 1

        _LOGGER.info("command %s executed successfully!", event.command.name)

