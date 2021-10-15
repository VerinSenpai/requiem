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


from extensions.politics_and_war import commands, background
from lib import client


def load(bot: client.Requiem) -> None:
    bot.add_slash_command(commands.InfraCost)
    bot.add_slash_command(commands.LandCost)
    bot.add_slash_command(commands.CityCost)
    bot.add_slash_command(commands.NationInfo)
    bot.add_plugin(background.Background(bot))


def unload(bot: client.Requiem) -> None:
    bot.remove_slash_command("infracost")
    bot.remove_slash_command("landcost")
    bot.remove_slash_command("citycost")
    bot.remove_slash_command("nationinfo")
    bot.remove_plugin("background")
