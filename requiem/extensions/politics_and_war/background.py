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


from lightbulb.ext import tasks
from pwpy import api


async def generate_identity_queries(api_key: str, query_handler: api.BulkQueryHandler) -> None:
    """
    Fetches page count for nations and alliances.
    Generates subsequent queries for identifying data.
    """
    query = """
    nations(first: 500) {
        paginatorInfo {
            lastPage
        }
    }
    alliances(first: 50) {
        paginatorInfo {
            lastPage
        }
    }
    """
    response = await api.fetch_query(api_key, query)

    nations_pages = response["nations"]["paginatorInfo"]["lastPage"]
    for page_number in range(nations_pages):
        query = """
        NATIONS_{0}: nations(first: 500, page: {0}) {{
            data {{
                nation_name
                leader_name
                id
                date
            }}
        }}
        """.format(str(page_number + 1))
        query_handler.add_query(query)

    alliances_pages = response["alliances"]["paginatorInfo"]["lastPage"]
    for page_number in range(alliances_pages):
        query = """
        ALLIANCES_{0}: alliances(first: 50, page: {0}) {{
            data {{
                name
                id
                acronym
            }}
        }}
        """.format(str(page_number + 1))
        query_handler.add_query(query)