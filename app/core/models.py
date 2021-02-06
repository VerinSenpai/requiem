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


class Guilds(tortoise.models.Model):
    """
    Base guild configuration model.
    """

    snowflake: int = tortoise.fields.BigIntField(pk=True)
    prefix: str = tortoise.fields.TextField()
    restore_roles: bool = tortoise.fields.BooleanField(default=False)
    auto_role: int = tortoise.fields.BigIntField(default=0)
    welcome_channel: int = tortoise.fields.BigIntField(default=0)
    welcome_message: str = tortoise.fields.TextField(default="")
    farewell_channel: int = tortoise.fields.BigIntField(default=0)
    farewell_message: str = tortoise.fields.TextField(default="")


class NationIndex(tortoise.models.Model):
    """
    Nation index model.
    """

    nation_id: int = tortoise.fields.IntField(pk=True)
    nation_name: str = tortoise.fields.TextField()
    leader_name: str = tortoise.fields.TextField()
    alliance_id: int = tortoise.fields.IntField()
    alliance_position: str = tortoise.fields.TextField()
    color: str = tortoise.fields.TextField()
    cities: int = tortoise.fields.IntField()
    vmode_turns: int = tortoise.fields.IntField()
    beige_turns: int = tortoise.fields.IntField()
    original_creation_date: str = tortoise.fields.TextField()
    latest_creation_date: str = tortoise.fields.TextField()
    snowflake: int = tortoise.fields.BigIntField(default=0)


class AllianceIndex(tortoise.models.Model):
    """
    Alliance index model.
    """

    alliance_id: int = tortoise.fields.IntField(pk=True)
    alliance_name: str = tortoise.fields.TextField()
    alliance_acronym: str = tortoise.fields.TextField()
    color: str = tortoise.fields.TextField()
