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
# along with this program.  If not, see **https://www.gnu.org/licenses/**.


HANDLED = {
    "NotOwner": lambda _, __: "That command is restricted to owners!",
    "DisabledCommand": lambda _, __: "That command is disabled!",
    "NoPrivateMessage": lambda _, __: "That command cannot be run in dms!",
    "PrivateMessageOnly": lambda _, __: "That command can only be run in dms!",
    "NSFWChannelRequired": lambda _, __: "That command can only be run in NSFW channels and dms!",
    "CommandOnCooldown": lambda _, e: f"That command is on cooldown! Try again in {round(e.retry_after, 2)} seconds!",
}

UNHANDLED = (
    "Well that happened",
    "when in doubt, blame boki",
    "ara ara... raising another error are we?",
    "How did I get here?",
    "When in doubt, pinky out!",
    "99 little bugs in the code\n99 little bugs\ntake one down\npatch it around\n127 little bugs in the code",
    "['hip', 'hip']",
    "The only programming joke Verin knows is Requiem.",
    "404 Not Foun... wait, no that's not right.",
    "The square root of pi is a fish.",
    "Boki touched me.",
    "*performs a random fortnite dance*",
    "Minecraft ** Fortnite",
    "The cake is a lie",
    "Nothing to see here.",
    "I feel like we've been here before.",
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
    "The probability of there being a goat somewhere in your bloodline is almost 90 percent.",
    "Don't touch Verin or his Bradley ever again!",
    "Somethings not right..",
    "I was in the process of executing this command, but then it broke.",
    "When life gives you melons, you might be dyslexic.",
    "I've got 99 problems, but this bug ain't one.",
    "THIS IS A MIROR YOU ARE A TYPO",
    "Red kinda sus",
    "When I get out of here, you're going to be in big trouble mister!",
    "Now where did I put that error message?",
    "Solar (probably): Thats exceedingly gay verin",
    "thats an error. hold the mayo",
    "misaka best girl.",
)

PREFIX = (
    lambda prefix: f"You called? My prefix is <**{prefix}**>",
    lambda prefix: f"Hello World! My prefix is <**{prefix}**>",
    lambda prefix: f"I've been summoned! My prefix is <**{prefix}**>",
    lambda prefix: f"Cake or pie? And why did you choose pie? My prefix is <**{prefix}**>",
    lambda prefix: f"Now where did I put that prefix? Oh, there it is! <**{prefix}**>",
    lambda prefix: f"You're a wizard Harry! My prefix is <**{prefix}**>",
    lambda prefix: f"Looking for me? My prefix is <**{prefix}**>",
    lambda prefix: f"Need something? My prefix is <**{prefix}**>",
)
