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


from requiem.core.config import PostgresConfig
from tortoise import Tortoise, connections
from pathlib import Path

import tortoise
import asyncpg
import logging
import aerich
import shutil


_LOGGER = logging.getLogger("requiem.db")


async def start_db(instance_path: Path, config: PostgresConfig):
    try:
        await Tortoise.init(config.tortoise)

        conn = connections.get("default")

        try:
            await conn.db_create()

        except tortoise.exceptions.OperationalError:
            pass

        _LOGGER.info("connection to postgres server successful! (%s)", str(config.url))

        migrations_path: Path = instance_path / "migrations"
        command = aerich.Command(tortoise_config=config.tortoise, location=str(migrations_path))

        if not migrations_path.exists():
            await command.init_db(True)

            return

        await command.init()

        try:
            update = await command.migrate()

            if not update:
                return

            await command.upgrade(True)

            _LOGGER.info("requiem has updated the database tables!")

        except AttributeError:
            _LOGGER.warning("requiem was unable to read the migration files! they will be recreated!")

            shutil.rmtree(migrations_path)

    except asyncpg.InvalidAuthorizationSpecificationError as exc:
        _LOGGER.warning("connection to postgres server failed! %s", str(exc))

        raise


async def stop_db():
    if not Tortoise._inited:
        return

    await Tortoise.close_connections()

    _LOGGER.info("connection to postgres server closed!")
