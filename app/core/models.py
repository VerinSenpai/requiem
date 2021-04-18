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

from datetime import datetime


class Guilds(tortoise.models.Model):
    """
    GuildConfig model.
    """

    snowflake: int = tortoise.fields.BigIntField(pk=True)
    prefix: str = tortoise.fields.TextField()
    restore_roles: bool = tortoise.fields.BooleanField(default=False)
    auto_role: int = tortoise.fields.BigIntField(default=0)
    welcome_channel: int = tortoise.fields.BigIntField(default=0)
    welcome_message: str = tortoise.fields.TextField(default="")
    farewell_channel: int = tortoise.fields.BigIntField(default=0)
    farewell_message: str = tortoise.fields.TextField(default="")


class Nations(tortoise.models.Model):
    """
    Nation index and event checking model.
    """

    nation_id: int = tortoise.fields.IntField(pk=True)
    nation_name: str = tortoise.fields.TextField()
    prev_nation_name: str = tortoise.fields.TextField(null=True)
    leader_name: str = tortoise.fields.TextField()
    prev_leader_name: str = tortoise.fields.TextField(null=True)
    alliance_id: int = tortoise.fields.IntField()
    alliance_position: str = tortoise.fields.TextField()
    score: int = tortoise.fields.IntField()
    vmode: int = tortoise.fields.IntField()
    beigeturns: int = tortoise.fields.IntField()
    color: str = tortoise.fields.TextField()
    date: datetime = tortoise.fields.DatetimeField()
    missiles: int = tortoise.fields.IntField()
    nukes: int = tortoise.fields.IntField()
    is_reroll: bool = tortoise.fields.BooleanField(default=False)
    is_deleted: bool = tortoise.fields.BooleanField(default=False)
    last_seen: datetime = tortoise.fields.DatetimeField(auto_now=True)


class AllianceHistory(tortoise.models.Model):
    """
    Nation alliance history model.
    """

    id: int = tortoise.fields.IntField(generated=True, pk=True)
    nation_id: int = tortoise.fields.IntField()
    alliance_id: int = tortoise.fields.IntField()
    date_recorded: datetime = tortoise.fields.DatetimeField(auto_now_add=True)


class Alliances(tortoise.models.Model):
    """
    Alliance index model.
    """

    alliance_id: int = tortoise.fields.IntField(pk=True)
    acronym: str = tortoise.fields.TextField()
    name: str = tortoise.fields.TextField()
    color: str = tortoise.fields.TextField()
    is_deleted: bool = tortoise.fields.BooleanField(default=False)
    last_seen: datetime = tortoise.fields.DatetimeField(auto_now=True)
