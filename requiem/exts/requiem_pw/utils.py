# This is part of Requiem
# Copyright (C) 2020  Verin Senpai

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


from datetime import datetime, UTC, timedelta
from tortoise.expressions import Q


def last_active_str(last_active: datetime) -> str:
    delta = datetime.now(UTC) - last_active
    minutes = int(delta.seconds // 60)

    if days := delta.days:
        if days > 1:
            return f"{days} days ago"
        return f"1 day ago"

    elif hours := int(minutes // 60):
        if hours > 1:
            return f"{hours} hours ago"
        return f"1 hour ago"

    elif minutes > 5:
        return f"{minutes} minutes ago"

    return "Now"


def nations_filter(query: str) -> Q:
    if query.isdigit():
        return Q(
            Q(id=query),
            Q(discord_id=query),
            join_type="OR"
        )

    return Q(
        Q(nation_name=query),
        Q(leader_name=query),
        join_type="OR"
    )
