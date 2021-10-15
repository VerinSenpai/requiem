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
from pwpy import api, exceptions
from lib import client, models
from lightbulb import plugins

import logging
import asyncio
import time


_LOGGER = logging.getLogger("requiem.extensions.pnw")


class Background(plugins.Plugin):

    """
    Handles various background processes for politics and war ranging from stowing identifying information to
    dispatching war notifications.
    """
    def __init__(self, bot: client.Requiem) -> None:
        super().__init__()
        self.bot = bot
        self.key = bot.credentials.pnw_api_key
        self.main_task = asyncio.create_task(self.gather_and_run_indexing_queries())

    def cog_unload(self) -> None:
        self.main_task.cancel()

    async def generate_identity_queries(self, query: api.BulkQueryHandler) -> None:
        """
        Fetches page count for nations and alliances.
        Generates subsequent queries for identifying data.
        """

        response = await api.fetch_query(self.key, queries.pages_query)

        nations_pages = response["nations"]["paginatorInfo"]["lastPage"]
        for page_number in range(nations_pages):
            nations_query = queries.nations_identity_query.format(str(page_number + 1))
            query.add_query(nations_query)

        alliances_pages = response["alliances"]["paginatorInfo"]["lastPage"]
        for page_number in range(alliances_pages):
            alliances_query = queries.alliances_identity_query.format(str(page_number + 1))
            query.add_query(alliances_query)

    @staticmethod
    async def generate_event_watch_queries(query: api.BulkQueryHandler) -> None:
        """
        Pulls all watch targets from database and calls respective methods to build queries.
        """

    async def gather_and_run_indexing_queries(self) -> None:
        """
        Calls for all queries to be created, fetches queries, and starts processing.
        """
        try:
            while not self.bot.is_alive:
                await asyncio.sleep(10)

            query = api.BulkQueryHandler(self.key)

            operations = (
                asyncio.create_task(self.generate_identity_queries(query)),
            )

            await asyncio.gather(*operations)

            response = await query.fetch_query()

            for key, group in response.items():
                for item in group["data"]:
                    if key.startswith("N"):
                        defaults = {"name": item["nation_name"].lower(),
                                    "leader": item["leader_name"].lower(),
                                    "date": item["date"]}
                        await models.NationsIndex.get_or_create(id=item["id"], defaults=defaults)

                    elif key.startswith("A"):
                        defaults = {"name": item["name"].lower()}
                        await models.AlliancesIndex.get_or_create(id=item["id"], defaults=defaults)

        except exceptions.InvalidToken as exc:
            _LOGGER.error(exc)

        except Exception as exc:
            _LOGGER.error("gather and run queries encountered an unhandled exception.", exc_info=exc)
