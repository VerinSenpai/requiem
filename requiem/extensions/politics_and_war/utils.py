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


def build_nation_info_fields(nation: dict, embed: hikari.Embed) -> None:
    embed.add_field(name="Name", value=nation["nation_name"])
    embed.add_field(name="Leader", value=nation["leader_name"])
    embed.add_field(name="Score", value=f"{nation['score']:,}")

    if nation["alliance"]:
        embed.add_field(name="Alliance", value=nation["alliance"]["name"])
        embed.add_field(name="Alliance Score", value=f"{nation['alliance']['score']:,}")
        embed.add_field(name="Alliance Position", value=nation["alliance_position"].title())

    embed.add_field(name="War Policy", value=nation["warpolicy"])
    embed.add_field(name="Domestic Policy", value=nation["dompolicy"])
    embed.add_field(name="Color", value=nation["color"].title())
    embed.add_field(name="Cities", value=nation["num_cities"])
    embed.add_field(name="Espionage Available", value=nation["espionage_available"])
    embed.add_field(name="Soldiers", value=f"{nation['soldiers']:,}")
    embed.add_field(name="Tanks", value=f"{nation['tanks']:,}")
    embed.add_field(name="Aircraft", value=f"{nation['aircraft']:,}")
    embed.add_field(name="Ships", value=f"{nation['ships']:,}")
    embed.add_field(name="Missiles", value=f"{nation['missiles']:,}")
    embed.add_field(name="Nukes", value=f"{nation['nukes']:,}")
    embed.set_thumbnail(nation["flag"])


async def lookup_nation(target: str or int) -> int:
    """
    Before you ask why i'm doing it like this, don't.
    """
    try:
        fetched = await models.NationsIndex.get_or_none(id=int(target))

    except ValueError:
        fetched = await models.NationsIndex.get_or_none(
            Q(Q(name=target), Q(leader=target), join_type="OR")
        )

    return fetched.id if fetched else None

