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


from requiem.core.config import RequiemConfig

import lightbulb
import abc


class RequiemPlugin(lightbulb.Plugin, abc.ABC):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._app: RequiemApp | None = None

    @property
    def app(self) -> "RequiemApp":
        if self._app is None:
            raise RuntimeError(
                "'RequiemPlugin.app' cannot be accessed before the plugin has been added to a 'RequiemApp' instance"
            )

        return self._app

    @app.setter
    def app(self, val: "RequiemApp") -> None:
        self._app = val
        self.create_commands()

    @property
    def bot(self) -> "RequiemApp":
        return self.app

    @property
    def config(self) -> RequiemConfig:
        return self.app.config
