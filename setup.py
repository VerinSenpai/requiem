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


from setuptools import setup, find_packages

import requiem


def parse_requirements_file(path):
    with open(path) as fp:
        dependencies = (d.strip() for d in fp.read().split("\n") if d.strip())
        return [d for d in dependencies if not d.startswith("#")]


setup(
    name="requiem",
    version=requiem.__version__,
    description="A purpose built discord bot for the Politics and War community.",
    author=requiem.__author__,
    license="GPL-3.0",
    url=requiem.__url__,
    packages=find_packages(),
    entry_points={"console_scripts": ["requiem = requiem.__main__:cli"]},
    install_requires=parse_requirements_file("requirements.txt")
)
