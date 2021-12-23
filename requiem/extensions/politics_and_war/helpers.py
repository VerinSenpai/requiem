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


from tortoise.query_utils import Q
from lib import models

import hikari


ALLIANCE_URL = "https://politicsandwar.com/alliance/id="
MESSAGE_URL = "https://politicsandwar.com/inbox/message/receiver="
NATION_URL = "https://politicsandwar.com/nation/id="


async def lookup_nation(target: str or int) -> int:
    """
    Search through the database for a given nation.
    """
    try:
        fetched = await models.NationsIndex.get_or_none(id=int(target))

    except ValueError:
        fetched = await models.NationsIndex.get_or_none(
            Q(Q(name=target), Q(leader=target), join_type="OR")
        )

    return fetched.id if fetched else None





