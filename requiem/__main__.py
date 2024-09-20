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

from hikari.internal.aio import get_or_make_loop, destroy_loop
from requiem.core.config import load_config, RequiemConfig
from requiem.core.db import start_db, stop_db
from hikari.internal.ux import init_logging
from requiem.core.app import RequiemApp
from pathlib import Path

import click
import logging
import os
import aiohttp
import asyncpg
import hikari


_LOGGER = logging.getLogger("requiem.main")


def parse_directory(_, __, data_path: Path) -> Path:
    if str(data_path.parent) == ".":
        raise click.BadParameter("You must specify a full path!")

    elif os.getcwd() in str(data_path):
        raise click.BadParameter("Instances may not be started in the Requiem install directory!!")

    return data_path


def parse_instance(ctx: click.Context, _, instance: str) -> Path:
    data_path: Path = ctx.params["data_dir"]
    instance_path: Path = data_path / instance

    if instance_path.parent != data_path:
        raise click.BadParameter("Use --data-dir to specify a data directory!")

    return instance_path


def prompt_debug(ctx: click.Context, _, debug: bool) -> logging.INFO | logging.DEBUG:
    no_prompt: bool = ctx.params["no_prompt"]

    if debug and not no_prompt:
        confirm = click.confirm("are you sure you wish to enable debugging? performance may be impacted!")

        if confirm:
            return logging.DEBUG

    return logging.INFO


@click.pass_context
def prompt_close(ctx: click.Context, exit_code: int) -> None:
    no_prompt: bool = ctx.parent.params["no_prompt"]
    _LOGGER.warning(f"requiem has closed with exit code {exit_code}!")

    if not no_prompt:
        click.pause("press any key to exit the script...")

    exit(exit_code)


def prompt_setup() -> None:
    click.echo(f"run 'requiem setup' to create or modify an instance configuration.")

    prompt_close(0)


def handle_crash(instance_path: Path, requiem: ..., exc: Exception) -> None:
    crash_report: str = (
        f"Requiem Crash Report\n\n"
        f"Analytics ----------\n"
        f"Session Time:     {...}\n"
        f"Commands:         {...}\n"
        f"Exceptions:       {...}\n"
        f"Date/Time:        {...}\n\n"
        f"Traceback ----------\n{...}"
    )

    error_path: Path = instance_path / "error_reports"
    report_file: Path = error_path / "crash_report_{}.txt"

    try:
        ...

    except:
        ...

    _LOGGER.critical("requiem has encountered a critical exception and crashed!", exc_info=exc)


@click.group()
@click.pass_context
@click.option(
    "--data-dir",
    default=click.get_app_dir("requiem"),
    type=click.Path(file_okay=False, path_type=Path),
    is_eager=True,
    show_default=True,
    help="Directory where Requiem instances are stored.",
    callback=parse_directory
)
@click.option(
    "--instance",
    default="requiem",
    show_default=True,
    help="Name of the instance to be configured or started.",
    callback=parse_instance
)
@click.option(
    "--no-prompt",
    is_flag=True,
    is_eager=True,
    help="Disable all confirmation prompts."
)
@click.option(
    "--debug",
    is_flag=True,
    help="Run Requiem in debug mode.",
    callback=prompt_debug
)
@click.option(
    "--allow-color",
    is_flag=True,
    default=True,
    help="Allow the use of color to denote level in console messages."
)
@click.option(
    "--force-color",
    is_flag=True,
    help="Force the use of color to denote level in console messages."
)
def cli(
    ctx: click.Context,
    data_dir: str,
    instance: str,
    no_prompt: bool,
    debug: logging.INFO | logging.DEBUG,
    allow_color: bool,
    force_color: bool,
) -> None:
    ctx.obj = {"config": None, "session": None}
    init_logging(debug, allow_color, force_color)


@cli.command()
@click.pass_context
def start(ctx: click.Context) -> None:
    data_path: Path = ctx.parent.params["data_dir"]

    if not data_path.exists():
        _LOGGER.warning("instance directory (%s) does not exist!", data_path)

        prompt_setup()

    instance: Path = ctx.parent.params["instance"]
    instance_path: Path = data_path / instance

    if not instance_path.exists():
        _LOGGER.warning("instance (%s) does not exist!", instance)

        prompt_setup()

    config: RequiemConfig | None = load_config(instance_path)

    if not config:
        prompt_setup()

    loop = get_or_make_loop()

    try:
        loop.run_until_complete(start_db(config.database))
        app = RequiemApp(config)
        app.run(close_loop=False)

    except asyncpg.InvalidAuthorizationSpecificationError:
        _LOGGER.warning("requiem was unable to connect to the database using the credentials provided!")

        prompt_setup()

    except hikari.GatewayServerClosedConnectionError as exc:
        _LOGGER.warning("requiem has closed because the gateway server closed the connection with code %s!", exc.code)

    except aiohttp.ClientConnectionError:
        _LOGGER.warning("requiem was unable to reach discord! check your internet connection and try again!")

    except hikari.UnauthorizedError:
        _LOGGER.warning("requiem was unable to connect using the provided discord token!")

        prompt_setup()

    except KeyboardInterrupt:
        _LOGGER.warning("requiem was closed using a keyboard interrupt! attempting to shutdown gracefully...")

    except Exception as exc:
        handle_crash(instance_path, ..., exc)

        prompt_close(1)

    finally:
        loop.run_until_complete(stop_db())
        destroy_loop(loop, _LOGGER)

    prompt_close(0)


if __name__ == "__main__":
    cli()
