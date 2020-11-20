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


import colorlog
import logging
import aiohttp
import discord
from core import config, bot


_LOGGER = logging.getLogger("requiem.main")


def main() -> None:
    """
    Main task. Initializes logging, loads configuration and starts bot.
    """
    colorlog.basicConfig(
        level=logging.INFO,
        format="%(log_color)s%(bold)s%(levelname)-1.1s%(thin)s %(asctime)23.23s %(bold)s%(name)s: "
        "%(thin)s%(message)s%(reset)s",
    )

    try:
        if bot_config := config.load():
            requiem = bot.Requiem(bot_config)
            requiem.run(bot_config.discord_token)

    except aiohttp.ClientConnectionError:
        _LOGGER.warning("requiem was unable to connect to discord!")

    except discord.PrivilegedIntentsRequired:
        _LOGGER.warning(
            "requiem was unable to login because requiem requires members intents but they were not enabled!"
        )

    except discord.LoginFailure:
        _LOGGER.warning(
            "requiem was unable to login because the provided discord token was invalid!"
        )

    except Exception as exc:
        _LOGGER.fatal(
            "requiem has encountered a critical exception and crashed!", exc_info=exc
        )

    _LOGGER.info("requiem will now close!")


if __name__ == "__main__":
    main()
