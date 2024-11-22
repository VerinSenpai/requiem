# This is part of Requiem
# Copyright (C) 2020  Verin Senpai
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import pathlib
import typing as t

from requiem.core.config import RequiemConfig
from requiem.core.messages import UNHANDLED_ERRORS, CHECK_FAILURE_ERRORS
from requiem import __install_path__

from datetime import datetime, timedelta
from random import choice
from lightbulb.ext import tasks
from lightbulb.internal import manage_application_commands

import abc
import lightbulb
import logging
import hikari
import typing
import importlib
import sys


_LOGGER = logging.getLogger("requiem.app")


class RequiemPlugin(lightbulb.Plugin, abc.ABC):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._app: RequiemApp | None = None

    @property
    def app(self) -> "RequiemApp":
        if self._app is None:
            raise RuntimeError(
                "'RequiemPlugin.app' cannot be accessed before the plugin has been added to a 'RequiemApp' instance"
            )

        return self._app

    @app.setter
    def app(self, val: "RequiemApp") -> None:
        self._app = val
        self.create_commands()

    @property
    def bot(self) -> "RequiemApp":
        return self.app

    @property
    def config(self) -> RequiemConfig:
        return self.app.config


class RequiemContext(lightbulb.Context, abc.ABC):

    def __init__(self, app: "RequiemApp") -> None:
        super().__init__(app)

        self._app: "RequiemApp" = app
        self._start_time: datetime = datetime.now()

    @property
    def app(self) -> "RequiemApp":
        """The ``RequiemApp`` instance the context is linked to."""
        return self._app

    @property
    def bot(self) -> "RequiemApp":
        """Alias for :obj:`~RequiemContext.app`."""
        return self.app

    @property
    def config(self) -> RequiemConfig:
        return self.app.config

    @property
    def elapsed(self) -> int:
        return int((datetime.now() - self._start_time).microseconds / 1000)

    @property
    def color(self) -> int:
        return hikari.Color.from_hex_code("0x9b59b6")


class SlashContext(lightbulb.SlashContext, RequiemContext, abc.ABC):
    ...


class RequiemApp(lightbulb.BotApp, abc.ABC):

    def __init__(self, config: RequiemConfig) -> None:
        self._config: RequiemConfig = config
        self._start_time: datetime = datetime.now()

        super().__init__(
            token=config.token or "",
            banner=None,
            owner_ids=config.owner_ids,
            default_enabled_guilds=config.guild_ids,
        )

        self.subscribe(hikari.StartingEvent, self.on_starting)
        self.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.subscribe(lightbulb.SlashCommandErrorEvent, self.on_command_error)
        self.subscribe(lightbulb.SlashCommandCompletionEvent, self.on_command_completion)

        tasks.load(self)

    @property
    def config(self) -> RequiemConfig:
        return self._config

    @property
    def session_time(self) -> timedelta:
        return datetime.now() - self._start_time

    @property
    def get_extensions(self) -> typing.Generator:
        extensions_dir = __install_path__ / "exts"

        return (
            extension.name
            for extension in extensions_dir.iterdir()
            if extension.name not in ("__init__.py", "__pycache__")
        )

    @staticmethod
    async def on_command_error(event: lightbulb.SlashCommandErrorEvent) -> None:
        context: RequiemContext = event.context
        command: lightbulb.Command = context.command
        exc_type, exception, trace = event.exc_info

        if isinstance(exception, hikari.HTTPResponseError):
            _LOGGER.warning(str(exception))

            return

        elif isinstance(exception, lightbulb.CommandInvocationError):
            response = f"{choice(UNHANDLED_ERRORS)}\n\nAn unexpected error occurred! Sorry about that!"

            _LOGGER.exception(
                "an unhandled exception occurred while executing command '%s'!",
                command.name,
                exc_info=exception.original
            )

        elif isinstance(exception, NotImplementedError):
            response = f"Command '{command.name}' is not yet ready for use!"

        else:
            response = CHECK_FAILURE_ERRORS.get(exc_type, str(exception))

            if callable(response):
                response = response(exception, command)

        embed = hikari.Embed(description=response, color=context.color)
        await context.respond(embed=embed)

    @staticmethod
    async def on_command_completion(event: lightbulb.SlashCommandCompletionEvent) -> None:
        context: RequiemContext = event.context

        _LOGGER.info(
            "command '%s %s' completed in '%sms'!",
            context.invoked_with,
            context.invoked.name,
            context.elapsed
        )

    async def get_slash_context(
        self,
        event: hikari.InteractionCreateEvent,
        command: lightbulb.SlashCommand,
        cls=SlashContext,
    ) -> SlashContext:
        return cls(self, event, command)

    def load_extensions(self, *extensions: str) -> None:
        for extension in extensions or self.get_extensions:
            self.load_extension(extension)

        _LOGGER.info(
            "%s extension(s) containing %s plugin(s) have been loaded!",
            len(self.extensions),
            len(self.plugins)
        )

    def load_extension(self, extension: str, *, in_reload=False):
        extension = extension.removesuffix(".py")
        extension_path = f"requiem.exts.{extension}"

        try:
            module = importlib.import_module(extension_path)

            if not hasattr(module, "load"):
                _LOGGER.warning("extension '%s' has no 'load' method!", extension)

                return

            module.load(self)
            self.extensions.append(extension)

            if not in_reload:
                _LOGGER.info("extension '%s' loaded!", extension)

        except Exception as exc:
            _LOGGER.error("extension '%s' encountered an error while loading!", extension, exc_info=exc)

    def unload_extensions(self, *extensions: str) -> None:
        for extension in extensions or self.extensions[::]:
            self.unload_extension(extension)

        if len(self.plugins) > 0:
            _LOGGER.warning("one or more extensions failed to remove their plugins on cleanup!")

    def unload_extension(self, extension: str, *, in_reload=True) -> None:
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

            if not in_reload:
                _LOGGER.info("extension '%s' unloaded!", extension)

        except Exception as exc:
            _LOGGER.error("extension '%s' encountered an exception while unloading!", extension, exc_info=exc)

    def reload_extension(self, extension: str) -> None:
        extension_path = f"requiem.exts.{extension}"

        if extension not in self.extensions:
            _LOGGER.warning("extension '%s' is not currently loaded!", extension)

            raise lightbulb.ExtensionNotLoaded

        old = sys.modules[extension_path]

        try:
            self.unload_extension(extension, in_reload=True)
            self.load_extension(extension, in_reload=True)

            _LOGGER.info("extension '%s' reloaded!", extension)

        except Exception as exc:
            sys.modules[extension_path] = old
            _LOGGER.error("extension '%s' encountered an exception while reloading!", extension, exc_info=exc)
            raise

        else:
            del old

    def reload_extensions(self, *extensions: str) -> dict:
        exceptions = {}

        for extension in extensions or self.extensions[::]:
            try:
                self.reload_extension(extension)

            except Exception as exc:
                exceptions[extension] = exc

        return exceptions

    async def resync_commands(self) -> None:
        await manage_application_commands(self)

    async def on_starting(self, _) -> None:
        self.load_extensions()

    async def on_stopping(self, _) -> None:
        self.unload_extensions()


