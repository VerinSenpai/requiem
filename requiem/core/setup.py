# This is part of Requiem
# Copyright (C) 2020  Verin Senpai
from contextlib import suppress

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

import click
import hikari
import aiohttp
import asyncio


def setup_exit_prompt():
    click.echo("setup was exited by the user! no progress has been saved!")


class RequiemSetup:

    def __init__(self, config: RequiemConfig = None):
        self.fail_count: int = 0
        self.config = config or {}

    async def get_token(self):
        while self.fail_count < 5:
            self.config["token"] = token = click.prompt("enter your discord token")

            bot = hikari.GatewayBot(token, banner=None)

            try:
                await bot.start(check_for_updates=False)

                return

            except hikari.UnauthorizedError:
                self.fail_count += 1

            finally:
                await bot.close()



async def run_setup():
    setup = RequiemSetup()
    await setup.get_token()
