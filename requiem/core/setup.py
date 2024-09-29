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

import click
import hikari
import asyncio
import aiohttp
import logging


_LOGGER = logging.getLogger("requiem.setup")


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
        while self.fail_count < 5:
            current_token: str | None = self.current.discord_token

            self.updated["token"] = token = click.prompt(
                "enter a discord token",
                default=current_token,
                show_default=bool(current_token)
            )

            _LOGGER.info("setup is validating the provided token with discord.")

            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    f"{urls.REST_API_URL}/users/@me",
                    headers={"Authorization": f"Bot {token}"}
                )

            if response.status == 200:
                _LOGGER.info("token passed validation. proceeding with setup.")

                return

            _LOGGER.info("the token provided could not be validated! check your input and try again!")

    async def run(self) -> None:
        await self.get_token()