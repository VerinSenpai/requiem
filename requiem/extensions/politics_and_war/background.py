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


from extensions.politics_and_war import queries
from lib import client, models, tasks
from pwpy import api, exceptions

import logging
import asyncio


_LOGGER = logging.getLogger("requiem.extensions.politics_and_war.background")


async def generate_identity_queries(api_key: str, query: api.BulkQueryHandler) -> None:
    """
    Fetches page count for nations and alliances.
    Generates subsequent queries for identifying data.
    """

    response = await api.fetch_query(api_key, queries.pages_query)

    nations_pages = response["nations"]["paginatorInfo"]["lastPage"]
    for page_number in range(nations_pages):
        nations_query = queries.nations_identity_query.format(str(page_number + 1))
        query.add_query(nations_query)

    alliances_pages = response["alliances"]["paginatorInfo"]["lastPage"]
    for page_number in range(alliances_pages):
        alliances_query = queries.alliances_identity_query.format(str(page_number + 1))
        query.add_query(alliances_query)


@tasks.loop(minutes=5)
async def gather_and_run_queries(bot: client.Requiem) -> None:
    """
    Calls for all queries to be created, fetches queries, and starts processing.
    """
    try:
        while not bot.is_alive:
            await asyncio.sleep(10)

        api_key = bot.credentials.pnw_api_key
        query = api.BulkQueryHandler(api_key)

        operations = (
            asyncio.create_task(generate_identity_queries(api_key, query)),
        )

        await asyncio.gather(*operations)

        response = await query.fetch_query()

        for key, group in response.items():
            for item in group["data"]:
                if key.startswith("N"):
                    defaults = {
                        "name": item["nation_name"].lower(),
                        "leader": item["leader_name"].lower(),
                    }
                    await models.NationsIndex.get_or_create(id=int(item["id"]), defaults=defaults)

    except exceptions.InvalidToken as exc:
        _LOGGER.warning(exc)

    except Exception as exc:
        _LOGGER.error("gather and run indexing queries encountered an unhandled exception.", exc_info=exc)
