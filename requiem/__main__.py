# This is part of Requiem
# Copyright (C) 2020  Verin Senpai
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from lightbulb import BotApp


import yaml
import attr

from pathlib import Path
from cattr import global_converter


instance_path: Path





@attr.s(auto_attribs=True)
class SessionTrack(ConfigBase):

    file_name = "session.yaml"

    boot_count: int = 0
    shut_count: int = 0
    diff_count: int = 0


@attr.s(auto_attribs=True)
class RequiemConfig(ConfigBase):
    discord_token: str = None
    guild_ids: list = []
    owner_ids: list = []
