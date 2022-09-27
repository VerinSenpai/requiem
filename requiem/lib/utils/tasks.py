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


import logging
import asyncio


_LOGGER = logging.getLogger("requiem.tasks")


class Task:

    def __init__(self, coro, time) -> None:
        self._coro = coro
        self._sleep_time = time
        self._task = None

    def start(self, *args, **kwargs):
        self._task = asyncio.create_task(self._loop(*args, **kwargs))

    def stop(self):
        if not self._task or self._task.done():
            return

        self._task.cancel()

    async def _loop(self, *args, **kwargs):
        try:
            while True:
                await self._coro(*args, **kwargs)
                await asyncio.sleep(self._sleep_time)

        except Exception as exc:
            _LOGGER.error("requiem encountered an exception while handling a task!", exc_info=exc)


def loop(*, seconds: int = 0, minutes: int = 0, hours: int = 0):
    time = seconds + (minutes * 60) + (hours * 3600)

    def decorator(coro):
        return Task(coro, time)

    return decorator
