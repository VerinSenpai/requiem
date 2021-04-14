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

from tortoise.query_utils import Q
from core import models
from . import errors


async def v3_post(session: aiohttp.ClientSession, key: str, query: str) -> dict:
    """
    Posts a request to the pnw graphql api.
    """
    payload = {"api_key": key, "query": query}

    async with session.get("https://api.politicsandwar.com/graphql", json=payload) as response:
        if response.status == 401:
            raise errors.InvalidAPIKey("There was an issue with the provided api key!")
        return await response.json(content_type="application/json")


async def nation_lookup(target: str or int) -> models.Nations:
    """
    Look up a nation using a string. Can be ID, user, name, or leader.
    """
    target = str(target).lower()

    if target.isnumeric():
        q = Q(id=target, snowflake=target, join_type="OR")

    else:
        q = Q(name__iexact=target, leader__iexact=target, join_type="OR")

    return await models.Nations.get_or_none(q)
