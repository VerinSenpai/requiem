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


from requiem.core.impl import RequiemApp
from requiem.exts.politics_and_war import commands, background


def load(app: RequiemApp):
    app.add_plugin(background.plugin)
    app.add_plugin(commands.plugin)
    background.update_indexes.start()


def unload(app: RequiemApp):
    background.update_indexes.stop()
    app.remove_plugin(background.plugin)
    app.remove_plugin(commands.plugin)
