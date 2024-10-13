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
from requiem.core.database import start_database, stop_database
from hikari.internal.ux import supports_color
from requiem.core.app import RequiemApp
from requiem.core.setup import RequiemSetup
from requiem import __version__
from functools import update_wrapper
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, QueueListener, QueueHandler
from colorlog.formatter import ColoredFormatter

import asyncio
import traceback
import click
import logging
import os
import aiohttp
import asyncpg
import hikari
import sys
import platform
import queue


_LOGGER = logging.getLogger("requiem.main")
_QUEUE_LISTENER: QueueListener | None = None


def init_logging(
    flavor: logging.INFO | logging.DEBUG,
    allow_color: bool,
    force_color: bool,
    instance_path: Path
) -> None:
    base_format = logging.Formatter("%(levelname)-1.1s (asctime)23.23s %(name)s: %(message)s")
    color_format = ColoredFormatter(
        fmt=(
            "%(log_color)s%(bold)s%(levelname)-1.1s%(thin)s "
            "%(asctime)23.23s "
            "%(bold)s%(name)s: "
            "%(thin)s%(message)s%(reset)s"
        ),
        force_color=True
    )
    stream_format = color_format if supports_color(allow_color, force_color) else base_format

    log_queue = queue.Queue()
    queue_handler = QueueHandler(log_queue)

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(stream_format)

    latest_file = logging.handlers.RotatingFileHandler(instance_path / "latest.log", maxBytes=1024)
    latest_file.setFormatter(base_format)

    logging.basicConfig(level=flavor, handlers=(queue_handler, stream_handler))

    global _QUEUE_LISTENER
    _QUEUE_LISTENER = QueueListener(log_queue, latest_file)
    _QUEUE_LISTENER.start()


def pass_parameters(*params):
    def decorator(func):
        @click.pass_context
        def wrapper(ctx: click.Context, *args, **kwargs):
            _params = {**ctx.params, **ctx.parent.params}
            selected = (_params.get(param) for param in params)
            return func(*selected, *args, **kwargs)
        return update_wrapper(wrapper, func)
    return decorator


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


@pass_parameters("no_prompt")
def prompt_close(no_prompt: bool, exit_code: int) -> None:
    _LOGGER.warning(f"requiem has closed with exit code {exit_code}!")

    if not no_prompt:
        click.pause("press any key to exit the script...")

    exit(exit_code)


def prompt_setup() -> None:
    click.echo(f"run 'requiem setup' to create or modify an instance configuration.")

    prompt_close(0)


@pass_parameters("instance")
def handle_crash(instance_path: Path, session: RequiemApp | RequiemSetup, exc: Exception) -> None:
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    current_time: datetime = datetime.now()

    crash_report: str = (
        f"Analytics         ----------\n"
        f"Date/Time         {current_time}\n"
        f"Session Time      {session.session_time}\n"
        f"Platform          {platform.platform()}\n"
        f"Python            {sys.version}\n"
        f"Requiem           {__version__}\n"
        f"Traceback         ----------\n{"".join(tb)}"
    )

    report_file: Path = instance_path / "crashes" / f"{current_time.strftime("%Y%m%d%H%M%S")}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(crash_report)

    _LOGGER.critical("requiem has encountered a critical exception and crashed!", exc_info=exc)


@click.group()
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
    data_dir: str,
    instance: Path,
    no_prompt: bool,
    debug: logging.INFO | logging.DEBUG,
    allow_color: bool,
    force_color: bool,
) -> None:
    if os.name != "nt":
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    init_logging(debug, allow_color, force_color, instance)


@cli.command()
@pass_parameters("data_dir", "instance")
def start(data_path: Path, instance_path: Path) -> None:
    if not data_path.exists():
        _LOGGER.warning("instance directory (%s) does not exist!", data_path)

        prompt_setup()

    if not instance_path.exists():
        _LOGGER.warning("instance (%s) does not exist!", instance_path.name)

        prompt_setup()

    config: RequiemConfig | None = load_config(instance_path)

    if not config:
        prompt_setup()

    loop: asyncio.AbstractEventLoop = get_or_make_loop()
    session = RequiemApp(config)

    try:
        loop.run_until_complete(start_database(instance_path, config.database))
        session.run(close_loop=False, check_for_updates=False)

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
        _LOGGER.warning("requiem was closed using a keyboard interrupt! shutting down gracefully...")

    except Exception as exc:
        handle_crash(session, exc)

        prompt_close(1)

    finally:
        loop.run_until_complete(stop_database())
        destroy_loop(loop, _LOGGER)

        _QUEUE_LISTENER.stop()

    prompt_close(0)


@cli.command()
@pass_parameters("data_dir", "instance")
def setup(data_path: Path, instance_path: Path) -> None:
    config: RequiemConfig = load_config(instance_path)

    if config:
        confirm: bool = click.confirm(f"config for instance '{instance_path.name}' already exists! continue?")

        if not confirm:
            prompt_close(0)

    if not instance_path.exists():
        click.echo(f"directory for instance '{instance_path.name}' will be created in location '{data_path}'!")

    instance_path.mkdir(parents=True, exist_ok=True)
    session = RequiemSetup(instance_path, config)

    try:
        session.run()

    except KeyboardInterrupt:
        _LOGGER.info("setup was closed using a keyboard interrupt! shutting down gracefully...")

    except Exception as exc:
        handle_crash(session, exc)

        prompt_close(1)

    finally:
        destroy_loop(session.loop, _LOGGER)

        _QUEUE_LISTENER.stop()

    prompt_close(0)


if __name__ == "__main__":
    cli()
