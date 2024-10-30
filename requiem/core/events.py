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


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from requiem.core.app import RequiemApp


from requiem.core.context import RequiemContext
from lightbulb import events

import attr
import abc


class RequiemEvent(events.LightbulbEvent, abc.ABC):
    """
    Subclass of 'events.LightbulbEvent' that implements requiem specific type hinting.
    """

    app: "RequiemApp" = attr.ib()

    @property
    def bot(self) -> "RequiemApp":
        return self.app


class CommandErrorEvent(events.CommandErrorEvent, RequiemEvent, abc.ABC):

    context: RequiemContext = attr.ib()


class SlashCommandErrorEvent(CommandErrorEvent, RequiemEvent, abc.ABC):
    ...


class CommandCompletionEvent(events.CommandCompletionEvent, RequiemEvent, abc.ABC):

    context: RequiemContext = attr.ib()


@attr.s(slots=True, weakref_slot=False)
class SlashCommandCompletionEvent(CommandCompletionEvent, RequiemEvent, abc.ABC):
    ...
