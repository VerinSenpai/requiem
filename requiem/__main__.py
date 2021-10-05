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
from lib import client, models

import logging
import aiohttp
import hikari
import typing
import yaml


_LOGGER = logging.getLogger("requiem.main")
T = typing.TypeVar("T")


def get_credentials() -> T:
    """
    Attempts to fetch credentials.yaml file.
    """
    try:
        _LOGGER.info("requiem is fetching the credentials file!")

        with open("credentials.yaml") as stream:
            data = yaml.safe_load(stream)

        credentials = global_converter.structure(data, models.Credentials)

        _LOGGER.info("requiem has successfully fetched the credentials file!")

        return credentials

    except FileNotFoundError:
        _LOGGER.warning("requiem was unable to find the credentials.yaml file!")

    except (TypeError, ValueError):
        _LOGGER.warning("requiem was unable to read the credentials.yaml file!")


def start_requiem_failsafe() -> None:
    """
    Starts Requiem. Ensures any and all exceptions that reach this point are logged neatly.
    """
    credentials = get_credentials()

    if not credentials:
        return

    try:
        requiem = client.Requiem(credentials)
        requiem.run()

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


if __name__ == "__main__":
    ux.init_logging("INFO", True, False)
    start_requiem_failsafe()
    _LOGGER.info("requiem has closed!")
    input()
