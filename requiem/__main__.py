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


from requiem import __version__
from lib import setup, client

import click
import importlib
import requests
import re


@click.group()
def cli() -> None:
    try:
        page = requests.get("https://raw.githubusercontent.com/GodEmpressVerin/requiem/main/requiem/__init__.py")
        match = re.findall(r"(?<=__version__ = ).*", page.text)

        if match:
            current_version = __version__
            latest_version = match[0].strip('"')

            if current_version != latest_version:
                click.echo(f"a newer version of requiem is available, consider upgrading to {latest_version}")

        else:
            click.echo("requiem was unable to check for updates!")

    except requests.ConnectionError:
        click.echo("requiem was unable to connect github to check for updates!")


@cli.command()
def version() -> None:
    """View the installed version of Requiem, Lightbulb, and Hikari."""
    click.echo(f"requiem ({__version__})")
    importlib.import_module("lightbulb.__main__")


@cli.command()
@click.option("--debug", help="Start Requiem in debug mode.", is_flag=True)
def start(debug: bool) -> None:
    """Run Requiem."""
    if debug:
        confirm = click.confirm("start requiem in debug mode? performance may be impacted!")

        if confirm:
            click.echo("starting requiem in debug mode!")

        else:
            debug = False

    client.start_failsafe(debug)


@cli.command()
def configure():
    """Run the Requiem configuration utility."""
    setup.run_config()


if __name__ == "__main__":
    client.start_failsafe(False)



