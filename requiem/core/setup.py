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



from requiem.core.config import RequiemConfig
from hikari import urls
from datetime import datetime, timedelta
from pathlib import Path

import os
import click
import asyncio
import aiohttp
import logging
import yaml


_LOGGER = logging.getLogger("requiem.setup")


def prompt_close():
    click.pause("press any key to exit the script...")

    exit(0)


class RequiemSetup:

    def __init__(self, config: RequiemConfig = None) -> None:
        self._start_time: datetime = datetime.now()
        self._fail_count: int = 0

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

            click.echo("token could not be validated! check your input and try again!")

            await asyncio.sleep(5)

        click.echo("failed to validate token within 5 attempts! setup is exiting!")

        prompt_close()

    async def setup_db(self) -> None:
        config: dict = self.config.get("database")

        while self._fail_count < 5:
            config["host"] = click.prompt("database host", default=config["host"], show_default=True)
            config["port"] = click.prompt("database port", default=config["port"], show_default=True)
            config["user"] = click.prompt("database user", default=config["user"], show_default=True)
            current: str | None = config["password"]
            config["password"] = click.prompt("database password", default=current, show_default=bool(current))

    async def run(self, instance_path: Path) -> None:
        config_file: Path = instance_path / "config.yaml"

        with config_file.open("w") as file:
            await self.get_token()
            self._fail_count = 0
            await self.setup_db()

            yaml.safe_dump(self.config, file)

        _LOGGER.info("setup is complete! config saved to '%s'!", config_file)

        confirm = click.confirm("would you like to create a run file?")

        if not confirm:
            return

        py_call = "python" if os.name == "nt" else "python3"
        ext = "bat" if os.name == "nt" else "sh"
        script: str = f"{py_call} -OO -m requiem start"

        with open(f"run_requiem.{ext}", "w") as file:
            file.write(script)

        _LOGGER.info("setup script created!")
