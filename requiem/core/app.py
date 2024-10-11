# This is part of Requiem
# Copyright (C) 2020  Verin Senpai
import typing as t

from lightbulb import context as context_, commands

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


from requiem.core.context import RequiemSlashContext, RequiemContext
from requiem.core.config import RequiemConfig
from datetime import datetime, timedelta
from requiem import exts
from pathlib import Path

import abc
import lightbulb
import logging
import hikari
import typing
import importlib
import sys


_LOGGER = logging.getLogger("requiem.app")


class RequiemApp(lightbulb.BotApp, abc.ABC):

    def __init__(self, config: RequiemConfig) -> None:
        self._start_time: datetime = datetime.now()

        super().__init__(
            token=config.token or "",
            banner=None,
            owner_ids=config.owner_ids,
            default_enabled_guilds=config.guild_ids,
        )

        self.subscribe(hikari.StartingEvent, self.handle_starting)
        self.subscribe(hikari.StoppingEvent, self.handle_stopping)
        self.subscribe(lightbulb.SlashCommandErrorEvent, self.handle_command_error)

    @property
    def session_time(self) -> timedelta:
        return datetime.now() - self._start_time

    @property
    def get_extensions(self) -> typing.Generator:
        extensions_dir = Path(exts.__file__).parent

        return (
            extension.name
            for extension in extensions_dir.iterdir()
            if extension.name not in ("__init__.py", "__pycache__")
        )

    async def handle_command_error(self, event: lightbulb.SlashCommandErrorEvent) -> None:
        ctx: RequiemContext = event.context
        exc_type, exception, trace = event.exc_info

        if isinstance(exception, lightbulb.CheckFailure):
            message: str = "check failure. not implemented yet."

        else:
            message: str = "Requiem encountered an error while executing "

        await ctx.respond(f"command error encountered! {exc_type}")

    async def get_slash_context(
        self,
        event: hikari.InteractionCreateEvent,
        command: commands.slash.SlashCommand,
        cls=RequiemSlashContext,
    ) -> RequiemSlashContext:
        return cls(self, event, command)

    def load_extensions(self, extension: str = None) -> None:
        if extension is None:
            for extension in self.get_extensions:
                self.load_extensions(extension)

            _LOGGER.info(
                "%s extension(s) containing %s plugin(s) have been loaded!",
                len(self.extensions),
                len(self.plugins)
            )

            return

        extension = extension.removesuffix(".py")
        extension_path = f"requiem.exts.{extension}"

        try:
            module = importlib.import_module(extension_path)

            if not hasattr(module, "load"):
                _LOGGER.warning("extension '%s' has no 'load' method!", extension)

                return

            module.load(self)
            self.extensions.append(extension)
            _LOGGER.info("extension '%s' loaded!", extension)

        except Exception as exc:
            _LOGGER.error("extension '%s' encountered an error while loading!", extension, exc_info=exc)

    def unload_extensions(self, extension: str = None):
        if extension is None:
            for extension in self.extensions:
                self.unload_extensions(extension)

            if len(self.plugins) > 0:
                _LOGGER.warning("one or more extensions failed to remove their plugins on cleanup!")

            return

        extension_path = f"requiem.exts.{extension}"

        try:
            module = importlib.import_module(extension_path)

            if not hasattr(module, "unload"):
                _LOGGER.info("extension '%s' has no 'unload' method!", extension)

                return

            module.unload(self)
            self.extensions.remove(extension)

            for module in sys.modules.copy():
                if extension_path in module:
                    del sys.modules[module]

            _LOGGER.info("extension '%s' unloaded!", extension)

        except Exception as exc:
            _LOGGER.error("extension '%s' encountered an exception while unloading!", extension, exc_info=exc)

    async def handle_starting(self, event: hikari.StartingEvent) -> None:
        self.load_extensions()

    async def handle_stopping(self, event: hikari.StoppingEvent) -> None:
        self.unload_extensions()
