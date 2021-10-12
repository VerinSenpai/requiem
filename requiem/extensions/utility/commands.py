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


from lightbulb import slash_commands

import hikari
import time


class Ping(slash_commands.SlashCommand):

    description: str = "Check the ping response time between Requiem sending and modifying a message."

    async def callback(self, ctx: slash_commands.SlashCommandContext) -> None:
        embed = hikari.Embed(description='Pinging...')

        start = time.monotonic()
        message = await ctx.respond(embed=embed)

        millis = (time.monotonic() - start) * 1000

        embed.description = ""
        embed.add_field(name="ACK", value=f"{int(millis)}ms")

        await message.edit(embed=embed)
