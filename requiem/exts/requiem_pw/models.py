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


from tortoise import Model, fields
from datetime import datetime


class Nations(Model):
    id: int = fields.IntField(primary_key=True)
    nation_name: str = fields.TextField()
    leader_name: str = fields.TextField()
    date: datetime = fields.DatetimeField()
    original_date: datetime = fields.DatetimeField()
    discord_id: int = fields.BigIntField(null=True)
