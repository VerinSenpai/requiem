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


import typing


class AutoCompleteIndex:

    __slots__: typing.List[str] = ["_index", "__index", "_history"]

    def __init__(self):
        self._index: set = set()
        self.__index: set = set()
        self._history: dict = dict()

    def __len__(self):
        return len(self._index)

    @staticmethod
    def _search(arg: str, iterable: typing.Iterable):
        for item in set(iterable):
            if item.startswith(arg) or arg in item:
                yield item.title()

    def insert(self, value: str) -> None:
        self.__index.add(value.lower())

    def update(self):
        self._index = self.__index
        self.__index = set()

    def search(self, arg: str, user: int, results: int = 5) -> list:
        if arg:
            results = list(self._search(arg.lower(), self._index))

            if arg.title() not in results:
                results.insert(0, arg.title())

        else:
            results = list(self._search("", self.history(user)))

        return results[:results]

    def record(self,  user: int, arg) -> None:
        arg = arg.lower()
        history = self.history(user)

        if arg not in history:
            if len(history) == 5:
                history.pop(5)

            history.insert(0, arg)
            self._history[user] = history

    def history(self, user: int) -> list:
        if user in self._history.keys():
            return self._history[user]
        return []
