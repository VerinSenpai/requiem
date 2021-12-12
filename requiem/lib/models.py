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
    token: str
    enabled_guilds: list = []
    pnw_api_key: str = ""
    postgres_host: str or int = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = ""


class Guilds(tortoise.Model):
    id: int = tortoise.fields.BigIntField(pk=True)
    pnw_ticket_aa: int = tortoise.fields.IntField(default=0)
    accept_tickets: int = tortoise.fields.BooleanField(default=False)


class NationsIndex(tortoise.Model):
    id: int = tortoise.fields.IntField(pk=True)
    name: str = tortoise.fields.TextField()
    leader: str = tortoise.fields.TextField()


class AlliancesIndex(tortoise.Model):
    id: int = tortoise.fields.IntField(pk=True)
    name: str = tortoise.fields.TextField()
    acronym: str = tortoise.fields.TextField()
