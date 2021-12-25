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


import lightbulb
import hikari
import logging


_LOGGER = logging.getLogger("requiem.extensions.management")


@lightbulb.command("terminate", "Terminate the bot.")
@lightbulb.implements(lightbulb.SlashCommand)
async def terminate(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(description="Requiem is shutting down!")
    await ctx.respond(embed=embed)
    await ctx.bot.close()


@lightbulb.option("extension", "The extension to be reloaded.")
@lightbulb.command("reload", "Attempt to reload an extension.")
@lightbulb.implements(lightbulb.SlashCommand)
async def reload(ctx: lightbulb.Context) -> None:
    extension = ctx.options.extension.replace(" ", "_")
    embed = hikari.Embed()

    try:
        ctx.bot.reload_extensions(f"extensions.{extension}")
        embed.description = f"The extension {extension} has been reloaded!!"

    except lightbulb.ExtensionNotLoaded:
        embed.description = f"The extension {extension} could not be reloaded because it is not loaded!"

    except Exception as exc:
        embed.description = f"The extension {extension} could not be reloaded because an unexpected exception was " \
                            f"encountered! If it was already loaded, it has not been changed!"
        _LOGGER.error(
            f"encountered an exception while attempting to load {extension}!",
            exc_info=exc,
        )

    await ctx.respond(embed=embed)


@lightbulb.option("extension", "The extension to be unloaded.")
@lightbulb.command("unload", "Attempt to unload an extension.")
@lightbulb.implements(lightbulb.SlashCommand)
async def unload(ctx: lightbulb.Context) -> None:
    extension = ctx.options.extension.replace(" ", "_")
    embed = hikari.Embed()

    try:
        ctx.bot.unload_extensions(f"extensions.{extension}")
        embed.description = f"The extension {extension} has been unloaded!!"

    except lightbulb.ExtensionNotLoaded:
        embed.description = f"The extension {extension} could not be unloaded because it is not loaded!"

    except Exception as exc:
        embed.description = f"The extension {extension} could not be unloaded because an unexpected exception was " \
                            f"encountered!"
        _LOGGER.error(
            f"encountered an exception while attempting to load {extension}!",
            exc_info=exc,
        )

    await ctx.respond(embed=embed)


@lightbulb.option("extension", "The extension to be loaded.")
@lightbulb.command("load", "Attempt to load an extension.")
@lightbulb.implements(lightbulb.SlashCommand)
async def load(ctx: lightbulb.Context) -> None:
    extension = ctx.options.extension.replace(" ", "_")
    embed = hikari.Embed()

    try:
        ctx.bot.load_extensions(f"extensions.{extension}")
        embed.description = f"The extension {extension} has been loaded!!"

    except lightbulb.ExtensionAlreadyLoaded:
        embed.description = f"The extension {extension} could not be loaded because it is not loaded!"

    except Exception as exc:
        embed.description = f"The extension {extension} could not be loaded because an unexpected exception was " \
                            f"encountered!"
        _LOGGER.error(
            f"encountered an exception while attempting to load {extension}!",
            exc_info=exc,
        )

    await ctx.respond(embed=embed)
