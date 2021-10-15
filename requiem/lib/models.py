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


@attr.s(auto_attribs=True)
class Credentials:
    """
    Config object.
    """

    token: str
    enabled_guilds: list = []
    pnw_api_key: str = ""
    postgres_host: str or int = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = ""


class NationsIndex(tortoise.Model):
    """
    NationsIndex tortoise model object.
    """
    id: int = tortoise.fields.IntField(pk=True)
    name: str = tortoise.fields.TextField()
    leader: str = tortoise.fields.TextField()
    creation_date: str = tortoise.fields.TextField()


class AlliancesIndex(tortoise.Model):
    """
    AlliancesIndex tortoise model object.
    """
    id: int = tortoise.fields.IntField(pk=True)
    name: str = tortoise.fields.TextField()
