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


import typing
import attr
import yaml
import logging

from cattr import global_converter


_LOGGER = logging.getLogger("requiem.config")
T = typing.TypeVar("T")


@attr.s(auto_attribs=True)
class PostgresConfig:
    """
    Postgres configuration object.
    """

    host: str or int = "localhost"
    port: int = 5432
    database: str = "postgres"
    user: str = "postgres"
    password: str = ""


@attr.s(auto_attribs=True)
class Config:
    """
    Bot configuration object.
    """

    discord_token: str
    default_prefix: str = "r!"
    owner_ids: typing.List[int] = attr.ib(factory=list)
    api_key: str = ""
    show_statuses: bool = True
    prefix_on_mention: bool = True
    report_errors: bool = True
    postgres: PostgresConfig = attr.ib(factory=PostgresConfig)


def load() -> T:
    """
    Loads the bots configuration from the config.yaml file.
    """
    try:
        with open("config.yaml") as fs:
            data = yaml.safe_load(fs)
        return global_converter.structure(data, Config)

    except (TypeError, ValueError, FileNotFoundError):
        _LOGGER.warning(
            "requiem is unable to start because you have not filled out the config.yaml file properly!"
        )
