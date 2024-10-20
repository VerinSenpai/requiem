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


import logging
import typing
import attr
import cattrs
import tortoise
import yaml
import yarl

from cattr import global_converter
from pathlib import Path


_LOGGER: logging.Logger = logging.getLogger("requiem.config")


@attr.s(auto_attribs=True)
class PnWConfig:
    api_key: str = None


@attr.s(auto_attribs=True)
class PostgresConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = None
    path: str = "/postgres"

    @property
    def url(self) -> yarl.URL:
        return yarl.URL.build(
            scheme="postgres",
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            path=self.path,
        )

    @property
    def tortoise(self) -> dict:
        return tortoise.generate_config(
            str(self.url),
            {"models": ["aerich.models", "requiem.core.models"]}
        )


@attr.s(auto_attribs=True)
class RequiemConfig:
    token: str | None = None
    guild_ids: typing.List[int] = []
    owner_ids: typing.List[int] = []
    database: PostgresConfig = attr.ib(factory=PostgresConfig)
    pnw: PnWConfig = attr.ib(factory=PnWConfig)


def load_config(instance_path: Path) -> RequiemConfig | None:
    config_file: Path = instance_path / "config.yaml"

    try:
        with config_file.open() as stream:
            data: dict = yaml.safe_load(stream)

        config: RequiemConfig = global_converter.structure(data, RequiemConfig)
        _LOGGER.info("config for instance (%s) has been loaded!", instance_path.name)

        return config

    except (TypeError, cattrs.ClassValidationError):
        _LOGGER.warning("config for instance (%s) could not be read!", instance_path.name)

    except FileNotFoundError:
        _LOGGER.warning("config for instance (%s) could not be found!", instance_path.name)


def save_config(instance_path: Path, config: RequiemConfig) -> None:
    config_file: Path = instance_path / "config.yaml"

    config: dict = global_converter.unstructure(config)

    with config_file.open("w") as file:
        yaml.safe_dump(config, file)

    _LOGGER.info("config saved to '%s'!", config_file)
