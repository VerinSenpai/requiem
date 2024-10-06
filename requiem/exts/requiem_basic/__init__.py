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


from requiem.core.app import RequiemApp
from requiem.exts.requiem_basic import utility, debug


def load(app: RequiemApp) -> None:
    app.add_plugin(utility.plugin)
    app.add_plugin(debug.plugin)


def unload(app: RequiemApp) -> None:
    app.remove_plugin(utility.plugin)
    app.remove_plugin(debug.plugin)
