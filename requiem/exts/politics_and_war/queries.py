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


GAME_DATE = {
    "model": "game_info",
    "query": "game_date"
}


NATIONS_PAGES = {
    "model": "nations",
    "args": {"first": 500, "page": 1},
    "query": {"paginatorInfo": "lastPage"}
}


ALLIANCES_PAGES = {
    "model": "alliances",
    "args": {"first": 50, "page": 1},
    "query": {"paginatorInfo": "lastPage"}
}


NATION_COMMAND = {
    "model": "nations",
    "args": None,
    "query": {
        "data": (
            "id",
            "nation_name",
            "leader_name",
            "score",
            {"alliance": ("id", "name")},
            {"cities": ("infrastructure", "land", "powered")},
            "population",
            "color",
            "war_policy",
            "domestic_policy",
            "flag",
            "date",
            "last_active",
            "soldiers",
            "tanks",
            "aircraft",
            "ships",
            "missiles",
            "nukes"
        )
    }
}
