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


pages_query = """
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


nations_identity_query = """
NATIONS_{0}: nations(first: 500, page: {0}) {{
    data {{
        nation_name
        leader_name
        id
        date
    }}
}}
"""


alliances_identity_query = """
ALLIANCES_{0}: alliances(first: 50, page: {0}) {{
    data {{
        name
        id
    }}
}}
"""


nation_score_query = """
nations(first: 1, id: {0}) {{
    data {{
        score
    }}
}}
"""


nation_lookup_query = """
nations(first: 1, id: {0}) {{
    data {{
        id
        alliance_id
        alliance_position
        alliance {{
            name
            score
        }}
        nation_name
        leader_name
        score
        warpolicy
        dompolicy
        color
        num_cities
        flag
        espionage_available
        last_active
        date
        soldiers
        tanks
        aircraft
        ships
        missiles
        nukes
        offensive_wars {{
            id
        }}
        defensive_wars {{
            id
        }}
    }}
}}
"""
