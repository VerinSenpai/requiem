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


from requiem.core.config import RequiemConfig
from requiem.exts.politics_and_war import queries
from pwpy.api import QueryWrapper
from pwpy.errors import QueryKeyError

import logging


_LOGGER = logging.getLogger("politics_and_war.wrapper")


SESSION: QueryWrapper | None = None


async def setup(config: RequiemConfig) -> None:
    api_key = config.pw.api_key

    if not api_key:
        _LOGGER.warning("no api key present! pw commands will be unavailable!")

        return

    wrapper = QueryWrapper(api_key)

    try:
        response = await wrapper.get_query(queries.GAME_INFO)
        game_date = response["gameInfo"]["game_date"]

        global SESSION
        SESSION = wrapper

        _LOGGER.info("pw session ready! game date %s", game_date)

    except QueryKeyError:
        _LOGGER.info("invalid api key! pw commands will be unavailable!")



