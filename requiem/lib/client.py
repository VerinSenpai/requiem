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


from lightbulb import slash_commands
from lib.models import Credentials

import lightbulb
import logging
import typing
import hikari
import abc
import os


_LOGGER = logging.getLogger("requiem.client")


class Requiem(lightbulb.Bot, abc.ABC):
    """
    Custom Requiem client based on lightbulb.Bot that overwrites and implements Requiem specific methods.
    """

    def __init__(self, credentials: Credentials) -> None:
        super().__init__(
            token=credentials.token,
            slash_commands_only=True,
            banner=None,
            default_enabled_guilds=credentials.enabled_guilds,
        )

        self.subscribe(hikari.StartingEvent, self.on_starting_event)
        self.subscribe(hikari.StoppingEvent, self.on_stopping_event)

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

    async def on_starting_event(self, event: hikari.StartingEvent) -> None:
        """
        Loads extensions prior to Requiem connecting to discord.
        Logs number of extensions loaded and number of commands gathered.
        """
        for extension in self.all_extensions:
            try:
                self.load_extension(f"extensions.{extension}")

            except Exception as exc:
                _LOGGER.error(f"encountered an exception while attempting to load {extension}!", exc_info=exc)

        _LOGGER.info(
            f"successfully loaded {len(self.extensions)} extension(s) and {len(self.slash_commands)} command(s)!"
        )

    async def on_stopping_event(self, event: hikari.StoppingEvent) -> None:
        """
        Handles extension unloading and cleanup while Requiem is closing.
        """
        _LOGGER.info("requiem is cleaning up!")

        for extension in self.extensions:
            try:
                self.unload_extension(extension)

            except Exception as exc:
                _LOGGER.error(f"encountered an exception while attempting to unload {extension}!", exc_info=exc)

        _LOGGER.info("requiem has finished cleanup!")
