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


from discord import Colour


prefix_responses = (
    lambda p: f"What'd I do? My prefix is {p}",
    lambda p: f"You called? My prefix is {p}",
    lambda p: f"Whats up doc? My prefix is {p}",
    lambda p: f"Now where'd I put that prefix again? Oh! There it is! {p}",
)


unhandled_errors = (
    "Solar (Probably): That's exceedingly gay Verin.",
    "There's a solution here I can feel it!",
    "Show me where the bad Boki touched you.",
    "Well that happened.",
    "When in doubt, blame Boki.",
    "Ara ara... raising another error are we?",
    "How did I get here?",
    "When in doubt, pinky out!",
    "99 little bugs in the code\n99 little bugs\ntake one down\npatch it around\n127 little bugs in the code",
    "['hip', 'hip']",
    "The only programming joke Verin knows is Requiem.",
    "404 Not Foun... wait, wrong error.",
    "The square root of pi is a fish.",
    "Boki touched me.",
    "The cake is a lie.",
    "Wanna see me do it again?" "I feel like we've been here before.",
    "Lugging a spy satellite to the nearest subway and asking them to toast it.",
    "Damned pagans and their interdimensional space gods!",
    "Roses are red\nsilent as a mouse\nyour door is unlocked\nI'm in your house",
    "Roses are red\nviolets are blue\njava.lang.ClassNotFoundException\non Thread-Local-2\nUh... I'm a python bot?",
    "How was I supposed to know pepsi and keyboards don't mix?",
    "Ha ha! Working bots, am I right?",
    "We can pretend this never happened, yeah?",
    "Its not like I meant to break... B-B-Baka",
    "Would you like fries with that?",
    "OwO Whats this\n*notices error*",
    "Verin Verin!\nYes Papa?\nWorking Code?\nNo papa...",
    "Who are you?!? Where are we? Are you kidnapping me?",
    "I bet you thought I wouldn't notice :eyes: I always notice :eye: :eye:",
    "Discord senpai... I don't feel too good.",
    "Don't take this the wrong way!",
    "Ah... Um? As you were.",
    "Don't touch Verin or his Bradley ever again!",
    "Somethings not right...",
    "I was in the process of executing this command, but then I decided to toast it instead.",
    "When life gives you melons, you might be dyslexic.",
    "I've got 99 problems and this bug is one of em.",
    "THIS IS A MIROR YOU ARE A TYPO",
    "Red kinda sus.",
    "Now where did I put that error message?",
    "That's an error. hold the mayo.",
    "I blame the weebs.",
    "Actually if you don't mind, it's just The Doctor."
)


handled_errors = {
    "NotOwner": lambda _, __: "That command is restricted to owners!",
    "DisabledCommand": lambda _, __: "That command is disabled!",
    "NoPrivateMessage": lambda _, __: "That command cannot be run in dms!",
    "PrivateMessageOnly": lambda _, __: "That command can only be run in dms!",
    "NSFWChannelRequired": lambda _, __: "That command can only be run in NSFW channels and dms!",
    "CommandOnCooldown": lambda _, e: f"That command is on cool down! Try again in {round(e.retry_after, 2)} seconds!",
}


colours = {
    "dark_blue": Colour.dark_blue,
    "dark_gold": Colour.dark_gold,
    "dark_green": Colour.dark_green,
    "dark_magenta": Colour.dark_magenta,
    "dark_orange": Colour.dark_orange,
    "dark_purple": Colour.dark_purple,
    "dark_red": Colour.dark_red,
    "dark_teal": Colour.dark_teal,
    "dark_grey": Colour.dark_grey,
    "darker_grey": Colour.darker_grey,
    "lighter_grey": Colour.lighter_grey,
    "light_grey": Colour.light_grey,
    "blue": Colour.blue,
    "gold": Colour.gold,
    "green": Colour.green,
    "magenta": Colour.magenta,
    "orange": Colour.orange,
    "purple": Colour.purple,
    "red": Colour.red,
    "teal": Colour.teal,
    "greyple": Colour.greyple,
    "random": Colour.random,
}
