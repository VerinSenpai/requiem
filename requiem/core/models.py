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


import tortoise
import attr


class Guilds(tortoise.models.Model):
    """
    Guild model for basic guild configuration.
    """

    snowflake: int = tortoise.fields.BigIntField()
    prefix: str = tortoise.fields.TextField()
    colour: str = tortoise.fields.TextField(default="purple")


@attr.s(auto_attribs=True)
class Credentials:
    """
    Config object.
    """

    discord_token: str
    default_prefix: str = "r!"
    owner_ids: list = []
    prefix_on_mention: bool = True
    report_errors: bool = True
    postgres_host: str or int = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = ""
