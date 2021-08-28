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


from extensions.politics_and_war import utils, queries
from discord.ext import commands, tasks
from core import models

import asyncio


class Background(commands.Cog):
    """
    Handles various background processes for politics and war ranging from stowing identifying information to
    dispatching war notifications.
    """

    def __init__(self, key: str) -> None:
        self.key = key
        self.perform_run.start()

    def cog_unload(self) -> None:
        self.perform_run.stop()

    async def generate_identity_queries(self, query: utils.BulkQueryHandler) -> None:
        """
        Fetches page count for nations and alliances.
        Generates subsequent queries for identifying data.
        """
        response = await utils.fetch_query(self.key, queries.pages_query)

        nations_pages = response["nations"]["paginatorInfo"]["lastPage"]
        for page_number in range(nations_pages):
            nations_query = queries.nations_identity_query.replace("PAGE", str(page_number + 1))
            query.add_query(nations_query)

        alliances_pages = response["alliances"]["paginatorInfo"]["lastPage"]
        for page_number in range(alliances_pages):
            alliances_query = queries.alliances_identity_query.replace("PAGE", str(page_number + 1))
            query.add_query(alliances_query)

    @staticmethod
    async def generate_event_watch_queries(query: utils.BulkQueryHandler) -> None:
        """
        Pulls all watch targets from database and calls respective methods to build queries.
        """
        all_entries = await models.PWNS.all()

    def build_event_query(self, entry: models.PWNS) -> str:
        data = []

    @tasks.loop(minutes=5)
    async def perform_run(self) -> None:
        """
        Calls for all queries to be created, fetches queries, and starts processing.
        """
        query = utils.BulkQueryHandler(self.key)

        operations = (
            asyncio.create_task(self.generate_identity_queries(query)),
        )

        await asyncio.gather(*operations)
        response = await query.fetch_query()

        nations = (value["data"] for key, value in response.items() if key.startswith("N"))
