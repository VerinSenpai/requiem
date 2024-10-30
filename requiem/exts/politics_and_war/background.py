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


from requiem.core.impl import RequiemPlugin
from requiem.core.models import AutoCompleteIndex
from requiem.exts.politics_and_war import queries

from pwpy import QueryWrapper, QueryKeyError
from lightbulb.ext import tasks

import logging


_LOGGER = logging.getLogger("pw.background")


NATIONS_INDEX = AutoCompleteIndex()
ALLIANCES_INDEX = AutoCompleteIndex()

plugin = RequiemPlugin("pw.background")
SESSION: QueryWrapper | None = None


async def setup():
    api_key: str | None = plugin.config.pw.api_key

    if api_key is None:
        _LOGGER.warning("an api key was not provided! pw commands and features will be unavailable!")
        update_indexes.stop()

        return

    try:
        session = QueryWrapper(api_key)
        response = await session.get_query(queries.GAME_DATE)
        game_date = response["game_info"]["game_date"]
        _LOGGER.info("api key authenticated! game date %s", game_date)
        global SESSION
        SESSION = session

    except QueryKeyError:
        _LOGGER.warning("the provided api key was invalid! pw commands and features will be unavailable!")
        update_indexes.stop()


@tasks.task(m=10)
async def update_indexes():
    if SESSION is None:
        await setup()

    query_obj = SESSION.bulk_query()
    query_obj.insert(queries.NATIONS_PAGES)
    query_obj.insert(queries.ALLIANCES_PAGES)

    response = await query_obj.get()
    nations_pages = response["nations"]["paginatorInfo"]["lastPage"]
    alliances_pages = response["alliances"]["paginatorInfo"]["lastPage"]

    query_obj = SESSION.bulk_query()
    for page in range(1, nations_pages + 1):
        index_query = {
            "name": f"nations_{page}",
            "model": "nations",
            "args": {"page": page, "first": 500},
            "query": {"data": ("nation_name", "id")}
        }
        query_obj.insert(index_query)

    for page in range(1, alliances_pages + 1):
        index_query = {
            "name": f"alliances_{page}",
            "model": "alliances",
            "args": {"page": page, "first": 500},
            "query": {"data": ("name", "id")}
        }
        query_obj.insert(index_query)

    response = await query_obj.get()

    nations = (
        nation
        for page in range(1, nations_pages + 1)
        for nation in response[f"nations_{page}"]["data"]
    )

    alliances = (
        alliance
        for page in range(1, alliances_pages + 1)
        for alliance in response[f"alliances_{page}"]["data"]
    )

    for nation in nations:
        NATIONS_INDEX.insert(nation["nation_name"])

    NATIONS_INDEX.update()

    for alliance in alliances:
        ALLIANCES_INDEX.insert(alliance["name"])

    ALLIANCES_INDEX.update()

    _LOGGER.info("indexes updated!")