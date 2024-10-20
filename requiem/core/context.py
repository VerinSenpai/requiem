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


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requiem.core.app import RequiemApp

from lightbulb.context import Context, ApplicationContext, SlashContext
from hikari.colors import Color
from datetime import datetime

import abc


class RequiemContext(Context, abc.ABC):

    def __init__(self, app: "RequiemApp") -> None:
        super().__init__(app)

        self._start_time: datetime = datetime.now()

    @property
    def exec_time(self) -> int:
        return int((datetime.now() - self._start_time).microseconds / 1000)

    @property
    def color(self) -> int:
        return Color.from_hex_code("0x9b59b6")


class RequiemApplicationContext(ApplicationContext, RequiemContext, abc.ABC):
    ...


class RequiemSlashContext(SlashContext, RequiemApplicationContext, abc.ABC):
    ...
