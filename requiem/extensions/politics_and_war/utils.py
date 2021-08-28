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


import aiohttp


async def fetch_query(key: str, query: str) -> dict:
    """
    Performs a query fetch to the gql api.
    """
    url = f"https://api.politicsandwar.com/graphql?api_key={key}"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": "{" + query + "}"}) as response:
            data = await response.json()

    try:
        return data["data"]
    except KeyError:
        return data["error"]


class BulkQueryHandler:
    """
    Handles building and fetching of bulk graphql queries.
    """
    def __init__(self, key: str) -> None:
        self.key = key
        self.queries = []

    def add_query(self, query) -> None:
        """
        Adds a gql query string to the bulk query.
        """
        self.queries.append(query)

    async def fetch_query(self) -> dict:
        """
        Combines all queries and fetches them in one go.
        """
        query = "\n".join(self.queries)
        return await fetch_query(self.key, query)
