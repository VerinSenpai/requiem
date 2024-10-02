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


from requiem.core.config import RequiemConfig, PostgresConfig, save_config
from requiem.core.database import start_database, stop_database
from requiem import __discord__
from hikari.internal.aio import get_or_make_loop
from hikari import urls
from datetime import datetime, timedelta
from pathlib import Path
from cattr import global_converter

import click
import asyncio
import aiohttp
import logging
import asyncpg
import time


_LOGGER = logging.getLogger("requiem.setup")


async def test_discord_token(token: str) -> bool:
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            f"{urls.REST_API_URL}/users/@me",
            headers={"Authorization": f"Bot {token}"}
        )

    return response.status == 200


async def test_database(instance_path: Path, config: PostgresConfig) -> bool:
    try:
        await start_database(instance_path, config)

        return True

    except asyncpg.InvalidAuthorizationSpecificationError:
        return False

    finally:
        await stop_database()


class RequiemSetup:

    def __init__(self, instance_path: Path, config: RequiemConfig) -> None:
        self._loop: asyncio.AbstractEventLoop = get_or_make_loop()
        self._start_time: datetime = datetime.now()
        self._fail_count: int = 0
        self.instance_path: Path = instance_path
        self.config: RequiemConfig = config or global_converter.structure({}, RequiemConfig)

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def session_time(self) -> timedelta:
        return datetime.now() - self._start_time

    def handle_fail(self, message: str):
        click.echo(f"{message} check your input and try again!")

        if self._fail_count >= 2:
            click.echo(f"having trouble? feel free to ask for help in the requiem support discord! {__discord__}")

        else:
            self._fail_count += 1

        time.sleep(5)

    def get_token(self) -> None:
        current: str | None = self.config.token

        while True:
            self.config.token = input_token = click.prompt(
                "discord token",
                default=current,
                show_default=bool(current)
            )

            passed: bool = self.loop.run_until_complete(test_discord_token(input_token))
            if passed: return

            self.handle_fail("validation of discord token failed!")

    def setup_database(self) -> None:
        config: PostgresConfig = self.config.database

        while True:
            config.host = click.prompt("host", default=config.host, show_default=True)
            config.port = click.prompt("port", default=config.port, show_default=True, type=int)
            config.user = click.prompt("user", default=config.user, show_default=True)
            config.password = click.prompt(
                "password",
                default=config.password,
                show_default=bool(config.password)
            )
            config.path = f"/{self.instance_path.name}"

            passed: bool = self.loop.run_until_complete(test_database(self.instance_path, config))
            if passed: return

            self.handle_fail("validation of database credentials failed!")

    def run(self) -> None:
        self.get_token()
        self.setup_database()
        save_config(self.instance_path, self.config)
