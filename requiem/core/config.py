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


import logging
import typing as t
import attr
import cattrs
import tortoise
import yaml
import yarl
import importlib

from cattr import global_converter
from pathlib import Path


__all__ = ["PostgresConfig", "RequiemConfig", "load_config", "save_config"]


_LOGGER: logging.Logger = logging.getLogger("requiem.config")
_EXTENSIONS = []
_MODELS = ["aerich.models"]


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
        return tortoise.generate_config(str(self.url), {"models": _MODELS})


class RequiemConfig:
    token: str | None = None
    guild_ids: t.List[int] = []
    owner_ids: t.List[int] = []
    database: PostgresConfig = attr.ib(factory=PostgresConfig)
    packages: list = ["requiem"]

    @classmethod
    def add_attr(cls, attr_name: str, new_attr: type) -> None:
        cls.__annotations__[attr_name] = new_attr
        setattr(cls, attr_name, attr.ib(factory=new_attr))

    @property
    def get_extensions(self):
        return _EXTENSIONS


def _process_extension(extension: Path) -> None:
    extension_path = ".".join(extension.with_suffix('').parts)

    if extension.name == "__pycache__":
        return

    elif extension.name == "__init__.py":
        return

    if extension.is_dir():
        for file in extension.iterdir():
            if file.name == "config.py":
                try:
                    module = importlib.import_module(f"{extension_path}.config")

                    if not hasattr(module, "Config"):
                        _LOGGER.warning("config for extension '%s' has no 'load' method!", extension_path)

                        return

                    RequiemConfig.add_attr(extension.name, module.load())

                except Exception as exc:
                    _LOGGER.error(
                        "config for extension '%s' encountered an exception during pre-load processing!",
                        extension_path,
                        exc_info=exc
                    )

            if file.name == "models.py":
                _MODELS.append(f"{extension_path}.models")

    _EXTENSIONS.append(extension_path)


def _process_packages(packages):
    for package in packages:
        package_dir = Path(package) / "exts"

        if not package_dir.is_dir():
            _LOGGER.warning("extension package '%s' was not found! is this package installed?", package)

            continue

        for extension in package_dir.iterdir():
            _process_extension(extension)


def load_config(instance_path: Path) -> RequiemConfig | None:
    config_file: Path = instance_path / "config.yaml"

    try:
        with config_file.open() as stream:
            data: dict = yaml.safe_load(stream)

        _process_packages(data.get("packages", ["requiem"]))
        attr.s(RequiemConfig, auto_attribs=True)
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
