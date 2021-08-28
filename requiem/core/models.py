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
import enum


class Guilds(tortoise.models.Model):
    """
    Guild model for basic guild configuration.
    """
    snowflake: int = tortoise.fields.BigIntField(pk=True)
    prefix: str = tortoise.fields.TextField()
    colour: str = tortoise.fields.TextField(default="purple")


class PWNS(tortoise.models.Model):
    """
    PWNS config model.
    """
    snowflake: int = tortoise.fields.BigIntField()
    target: int = tortoise.fields.IntField()
    is_nation: bool = tortoise.fields.BooleanField(default=False)
    defensive_war: int = tortoise.fields.BigIntField(default=0)
    defensive_war_battle: int = tortoise.fields.BigIntField(default=0)
    offensive_war: int = tortoise.fields.BigIntField(default=0)
    offensive_war_battle: int = tortoise.fields.BigIntField(default=0)
    defensive_nuke: int = tortoise.fields.BigIntField(default=0)
    offensive_nuke: int = tortoise.fields.BigIntField(default=0)
    defensive_missile: int = tortoise.fields.BigIntField(default=0)
    offensive_missile: int = tortoise.fields.BigIntField(default=0)
    enters_beige: int = tortoise.fields.BigIntField(default=0)
    gains_beige: int = tortoise.fields.BigIntField(default=0)
    exits_beige: int = tortoise.fields.BigIntField(default=0)
    enters_vmode: int = tortoise.fields.BigIntField(default=0)
    gains_vmode: int = tortoise.fields.BigIntField(default=0)
    exits_vmode: int = tortoise.fields.BigIntField(default=0)
    changed_colours: int = tortoise.fields.BigIntField(default=0)
    has_deleted: int = tortoise.fields.BigIntField(default=0)
    has_rerolled: int = tortoise.fields.BigIntField(default=0)


class NationsIndex(tortoise.models.Model):
    """
    Nation index model.
    """
    id: str = tortoise.fields.TextField()
    name: str = tortoise.fields.TextField()
    leader: str = tortoise.fields.TextField()
    original_creation_date: str = tortoise.fields.TextField()
    latest_creation_date: str = tortoise.fields.TextField()
    alliance: int = tortoise.fields.IntField()
    alliance_position: int = tortoise.fields.IntField()
    snowflake: str = tortoise.fields.TextField()
    vacation: int = tortoise.fields.IntField()
    beige: int = tortoise.fields.IntField()
    color: str = tortoise.fields.TextField()


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
    pw_api_key: str = ""



