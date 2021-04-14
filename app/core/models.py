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
    alliance_id: int = tortoise.fields.IntField()
    alliance_position: str = tortoise.fields.TextField()
    nation_name: str = tortoise.fields.TextField()
    prev_nation_name: str = tortoise.fields.TextField(null=True)
    leader_name: str = tortoise.fields.TextField()
    prev_leader_name: str = tortoise.fields.TextField(null=True)
    color: str = tortoise.fields.TextField()
    vmode: int = tortoise.fields.IntField()
    beigeturns: int = tortoise.fields.IntField()
    date: datetime = tortoise.fields.DatetimeField()
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
