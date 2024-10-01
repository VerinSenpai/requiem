# This is part of Requiem
# Copyright (C) 2020  Verin Senpai

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



from requiem.core.config import RequiemConfig, PostgresConfig
from requiem.core.database import start_database
from requiem import __discord__
from hikari import urls
from datetime import datetime, timedelta
from pathlib import Path
from cattr import global_converter

import click
import asyncio
import aiohttp
import logging
import yaml
import asyncpg
import contextlib


_LOGGER = logging.getLogger("requiem.setup")


class RequiemSetup:

    def __init__(self, instance_path: Path, config: RequiemConfig) -> None:
        self._start_time: datetime = datetime.now()
        self._fail_count: int = 0
        self.instance_path: Path = instance_path
        config: RequiemConfig = config or global_converter.structure({}, RequiemConfig)
        self.config = config.__dict__
        self.config["database"] = config.database.__dict__

    @property
    def session_time(self) -> timedelta:
        return datetime.now() - self._start_time

    async def get_token(self) -> None:
        current: str | None = self.config.get("token")

        while self._fail_count < 5:
            self.config["token"] = input_token = click.prompt(
                "discord token", default=current, show_default=bool(current)
            )

            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    f"{urls.REST_API_URL}/users/@me",
                    headers={"Authorization": f"Bot {input_token}"}
                )

            if response.status == 200:
                return

            elif self._fail_count < 4:
                click.echo("token could not be validated! check your input and try again!")
                await asyncio.sleep(5)

            self._fail_count += 1

        click.echo("failed to validate token within 5 attempts!")

    async def setup_database(self) -> None:
        config: dict = self.config.get("database")

        while self._fail_count < 5:
            config["host"] = click.prompt("database host", default=config["host"], show_default=True)
            config["port"] = click.prompt("database port", default=config["port"], show_default=True)
            config["user"] = click.prompt("database user", default=config["user"], show_default=True)
            config["password"] = click.prompt(
                "database password", default=config["password"], show_default=bool(config["password"])
            )
            config["path"] = f"/{self.instance_path.name}"

            test_config: PostgresConfig = global_converter.structure(config, PostgresConfig)

            with contextlib.suppress(asyncpg.InvalidAuthorizationSpecificationError):
                await start_database(self.instance_path, test_config)
                self.config["database"] = config
                return

            if self._fail_count < 4:
                click.echo("database config could not be validated! check your inputs and try again!")
                await asyncio.sleep(5)

            self._fail_count += 1

        click.echo("failed to validate database credentials within 5 attempts!")

    async def run(self) -> None:
        config_file: Path = self.instance_path / "config.yaml"

        process = (
            self.get_token,
            self.setup_database
        )

        with config_file.open("w") as file:
            for job in process:
                self._fail_count = 0
                await job()

                if self._fail_count == 5:
                    click.echo(f"you appear to be having difficulty with setup! if you need assistance,\n"
                               f"feel free to ask for help in the requiem support server!\n\n{__discord__}")

                    _LOGGER.warning("setup aborted! no changes have been saved!")
                    return

            yaml.safe_dump(self.config, file)

        _LOGGER.info("setup is complete! config saved to '%s'!", config_file)
