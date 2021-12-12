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


from extensions.verins_lunchbox import commands
from lib import client

import lightbulb


plugin = lightbulb.Plugin("VerinsLunchbox")
plugin.command(commands.neko)
plugin.command(commands.foxgirl)


def load(requiem: client.Requiem) -> None:
    requiem.add_plugin(plugin)


def unload(requiem: client.Requiem) -> None:
    requiem.remove_plugin(plugin)
