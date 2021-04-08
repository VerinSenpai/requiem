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
import datetime


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
    Nation index model.
    """

    id: int = tortoise.fields.IntField(pk=True)
    deleted: bool = tortoise.fields.BooleanField(default=False)
    reroll: bool = tortoise.fields.BooleanField(default=False)
    name: str = tortoise.fields.TextField()
    prev_name: str = tortoise.fields.TextField(default="")
    leader: str = tortoise.fields.TextField()
    prev_leader: str = tortoise.fields.TextField(default="")
    alliance: int = tortoise.fields.IntField()
    alliance_position: str = tortoise.fields.TextField()
    war_policy: str = tortoise.fields.TextField()
    dom_policy: str = tortoise.fields.TextField()
    color: str = tortoise.fields.TextField()
    cities: int = tortoise.fields.IntField()
    score: int = tortoise.fields.IntField()
    vmode_turns: int = tortoise.fields.IntField()
    beige_turns: int = tortoise.fields.IntField()
    creation_date: str = tortoise.fields.TextField()
    soldiers: int = tortoise.fields.IntField()
    tanks: int = tortoise.fields.IntField()
    aircraft: int = tortoise.fields.IntField()
    ships: int = tortoise.fields.IntField()
    missiles: int = tortoise.fields.IntField()
    nukes: int = tortoise.fields.IntField()
    snowflake: int = tortoise.fields.BigIntField(default=0)
    last_updated: datetime.datetime = tortoise.fields.DatetimeField()


class Cities(tortoise.models.Model):
    """
    City index model.
    """
    id: int = tortoise.fields.IntField(pk=True)
    nation: int = tortoise.fields.IntField()
    name: str = tortoise.fields.TextField()
    date: datetime.datetime = tortoise.fields.DatetimeField()
    powered: bool = tortoise.fields.BooleanField()
    infra: int = tortoise.fields.IntField()
    land: int = tortoise.fields.IntField()
    nuclearpower: int = tortoise.fields.IntField()
    oilpower: int = tortoise.fields.IntField()
    coalpower: int = tortoise.fields.IntField()
    windpower: int = tortoise.fields.IntField()
    bauxitemine: int = tortoise.fields.IntField()
    coalmine: int = tortoise.fields.IntField()
    ironmine: int = tortoise.fields.IntField()
    leadmine: int = tortoise.fields.IntField()
    oilwell: int = tortoise.fields.IntField()
    uramine: int = tortoise.fields.IntField()
    farm: int = tortoise.fields.IntField()
    aluminumrefinery: int = tortoise.fields.IntField()
    munitionsfactory: int = tortoise.fields.IntField()
    steelmill: int = tortoise.fields.IntField()
    gasrefinery: int = tortoise.fields.IntField()
    hospital: int = tortoise.fields.IntField()
    policestation: int = tortoise.fields.IntField()
    recyclingcenter: int = tortoise.fields.IntField()
    subway: int = tortoise.fields.IntField()
    mall: int = tortoise.fields.IntField()
    bank: int = tortoise.fields.IntField()
    supermarket: int = tortoise.fields.IntField()
    stadium: int = tortoise.fields.IntField()
    barracks: int = tortoise.fields.IntField()
    airforcebase: int = tortoise.fields.IntField()
    drydock: int = tortoise.fields.IntField()
    factory: int = tortoise.fields.IntField()
    last_updated: datetime.datetime = tortoise.fields.DatetimeField()


class Alliances(tortoise.models.Model):
    """
    Alliance index model.
    """

    id: int = tortoise.fields.IntField(pk=True)
    deleted: bool = tortoise.fields.BooleanField(default=False)
    name: str = tortoise.fields.TextField()
    prev_name: str = tortoise.fields.TextField(default="")
    acronym: str = tortoise.fields.TextField()
    prev_acr: str = tortoise.fields.TextField(default="")
    score: int = tortoise.fields.IntField()
    color: str = tortoise.fields.TextField()
    flag: str = tortoise.fields.TextField()
    forum: str = tortoise.fields.TextField()
    irc: str = tortoise.fields.TextField()
    last_updated: datetime.datetime = tortoise.fields.DatetimeField()

