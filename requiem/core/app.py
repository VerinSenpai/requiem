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


from requiem.core.config import RequiemConfig

import abc
import lightbulb
import logging


_LOGGER = logging.getLogger("requiem.app")


class RequiemApp(lightbulb.BotApp, abc.ABC):

    def __init__(self, config: RequiemConfig) -> None:
        super().__init__(
            token=config.discord_token,
            banner=None,
            owner_ids=config.owner_ids,
            default_enabled_guilds=config.guild_ids
        )
