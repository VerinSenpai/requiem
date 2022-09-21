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


from requiem import __discord__
from lib import client

import yaml
import click
import yarl


def _get_discord_token():
    while True:
        click.echo("enter your discord token.")

        value = input()

        if value != "":
            return value

        click.echo("a discord token is required for requiem to run!")


def _get_postgres_host():
    while True:
        click.echo(
            "enter an ip or url to use for accessing the postgres server or press enter to continue."
            "defaults to localhost."
        )

        value = input()

        if " " in value:
            click.echo("the ip or url should not have any spaces!")

        elif value == "":
            return "localhost"

        else:
            return value


def _get_postgres_port():
    while True:
        click.echo(
            "enter a port to use for accessing the postgres server or press enter to continue."
            "defaults to 5432."
        )

        value = input()

        if not value.isdigit():
            click.echo("the value provided was not an integer and thus not a port number.")

        elif value == "":
            return 5432

        else:
            return value


def _get_postgres_user():
    while True:
        click.echo(
            "enter a username to use for accessing the postgres server or press enter to continue."
            "defaults to postgres."
        )

        value = input()

        if " " in value:
            click.echo("the postgres username should not have any spaces!")

        elif value == "":
            return "postgres"

        else:
            return value


def _get_postgres_password():
    while True:
        click.echo(
            "enter a password to use for accessing the postgres server or press enter to continue."
            "defaults to postgres."
        )

        value = input()

        if " " in value:
            click.echo("the postgres password should not have any spaces!")

        elif value == "":
            return "postgres"

        else:
            return value


def _get_postgres_database():
    while True:
        click.echo(
            "enter a database to use for accessing the postgres server or press enter to continue."
            "defaults to localhost."
        )

        value = input()

        if " " in value:
            click.echo("the postgres database should not have any spaces!")

        elif value == "":
            return "postgres"

        else:
            return value


def _get_database_url():
    confirm = click.confirm("would you like for requiem to connect to a dedicated postgres server?")

    if confirm:
        return yarl.URL.build(
            scheme="postgres",
            host=_get_postgres_host(),
            port=_get_postgres_port(),
            user=_get_postgres_user(),
            password=_get_postgres_password(),
            path=f"/{_get_postgres_database()}",
        )

    return "sqlite://db.sqlite3"


def run_config() -> None:
    """Build the config file and all required directories."""
    data_dir = client.DATA_DIR

    if not data_dir.is_dir():
        click.echo("requiem was unable to find the app data directory! it will be created!")

        try:
            data_dir.mkdir(parents=True, exist_ok=True)

        except PermissionError:
            click.echo("requiem was unable to create the app data directory!")

            return

    try:
        with open(data_dir / "config.yaml") as stream:
            yaml.safe_load(stream)

        confirm = click.confirm("requiem has found an existing config! would you like to overwrite it?")

        if not confirm:
            click.echo("configuration already exists! aborting...")

            return

    except FileNotFoundError:
        click.echo("requiem was unable to find the configuration! it will be created!")

    click.echo("values provided are not tested for validity during configuration!")
    click.echo(
        "if you need assistance, feel free to reach out on the requiem support server!"
        f"{__discord__}"
    )

    data = {
        "discord_token": _get_discord_token(),
        "database_url": _get_database_url()
    }

    try:
        with open(data_dir / "config.yaml", "w") as stream:
            yaml.safe_dump(data, stream)

        click.echo(f"the configuration is located at `{data_dir}`!\nyou may now start requiem.")

    except PermissionError:
        click.echo("requiem was unable to create the configuration file!")

        return
