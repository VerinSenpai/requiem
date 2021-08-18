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


from core import client, config

import tortoise
import colorlog
import discord
import logging
import asyncio
import aiohttp
import asyncpg
import socket
import yarl


_LOGGER = logging.getLogger("requiem.main")


async def setup_database(credentials: config.Credentials) -> None:
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
    modules = {"models": ["core.models"]}

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


def setup_logging() -> None:
    """
    Sets up logging with a basic config. Removes error log spam from shard logging.
    """
    colorlog.basicConfig(
        level=logging.INFO,
        format="%(log_color)s%(bold)s%(levelname)-1.1s%(thin)s %(asctime)23.23s %(bold)s%(name)s: "
        "%(thin)s%(message)s%(reset)s",
    )

    class ErrorSpamFilter(logging.Filter):
        """
        Removes exc_info from a logging entry.
        """
        def filter(self, record) -> bool:
            record.exc_info = None
            return True

    shard_logger = colorlog.getLogger("discord.shard")
    shard_logger.addFilter(ErrorSpamFilter())


def start():
    """"""
    setup_logging()
    credentials = config.get_config()

    if not credentials:
        return

    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_database(credentials))
    requiem = client.Requiem(credentials)

    try:
        requiem.run(credentials.discord_token)

    except KeyboardInterrupt:
        _LOGGER.error("requiem was closed out with a keyboard interrupt!")

    except aiohttp.ClientConnectionError:
        _LOGGER.error(
            "requiem is unable to connect to discord because of a connection issue!"
        )

    except discord.PrivilegedIntentsRequired as exc:
        _LOGGER.error(
            "requiem is unable to connect to discord because of missing privileged intents!"
        )

    except discord.LoginFailure:
        _LOGGER.error(
            "requiem is unable to connect to discord because of an invalid token!"
        )

    except Exception as exc:
        _LOGGER.error(
            "requiem encountered a critical exception and crashed!", exc_info=exc
        )

    if not requiem.is_closed():
        loop.run_until_complete(requiem.close())


def main():
    """
    Calls start method. Halts terminal on exit so user can read logs.
    """
    start()
    _LOGGER.info("requiem has closed!")
    input()


if __name__ == "__main__":
    main()
