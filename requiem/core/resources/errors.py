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


import lightbulb


CHECK_FAIL = {
    lightbulb.NotOwner: f"This command is restricted to Requiem owners!",
    lightbulb.CommandIsOnCooldown: lambda err, ctx: f"Command is on cooldown! Try again in {err.retry_after} seconds!",
    lightbulb.NSFWChannelOnly: "This command is restricted to NSFW channels!",
    lightbulb.HumanOnly: "Requiem does not support usage by other bots.",
    lightbulb.OnlyInGuild: "This command is restricted to server use only!",
    lightbulb.OnlyInDM: "This command is restricted to DM use only!"
}

UNHANDLED = (
    "Lugging a spy satellite to the nearest subway and asking them to toast it.",
    "Damned pagans and their interdimensional space gods!",
    "error. miku",
    "roses are red, silent as a mouse, your door is unlocked, im in your house",
    "roses are red\nviolets are blue\njava.lang.ClassNotFoundException\non Thread-Local-2\nWait I'm a python bot?",
    "**Number 15** Anime Foot Fungus\n\nThe last thing you want in your fan service anime is Verin's foot fungus,\n "
    "but as it turns out, that just might be what you get",
    "Whats up Doc? Something broke...",
    "Only you can prevent broken bots!",
    "Don't let ratty find out...",
    "Oh I'm sorry? Were you expecting a FUNCTIONAL bot?",
    "Bots broken, Apply more sebisauce to fix...",
    "Whoops that wasn't supposed to happen...",
    "The cake is a lie",
    "How was I supposed to know pepsi and keyboards don't mix?",
    "Show me where the bad Boki touched you...",
    "Ha Ha! Working bots, am I right?",
    "99 little bugs in the code. 99 little bugs. Take one down, patch it around. 127 little bugs in the code...",
    "We can pretend this never happened... right?",
    "404 Not Found! Wait... No that's not right...",
    "'insert bad joke here'",
    "I'm trying to fix the problems I created when I tried to fix the problems\n"
    "I created when I tried to fix the problems I created when I...",
    "Its not like I meant to break... B-B-Baka",
    "Somebody call an exterminator! There are bugs in the code!",
    "What is the square root of a fish? Now I'm sad...",
    "Your mouse has quit working, click OK to continue...",
    "Would you like fries with that?",
    "I'm a submarine! Wheres the cheese?",
    "Tried multiplying by the square root of the 64bit integer limit\nFailed miserably",
    "OwO Whats this\n*notices error*",
    "They see me breakin... they hatinn",
    "Now where did I put that error message...? Ah! There it is...",
    "Niko, lets go bowling!",
    "Must not be enough cat girls to spin the cogs, guess I'll die now.",
    "Where them errors at? Oh! There they are...",
    "Verin Verin!\nYes Papa?\nWorking Code?\nNo papa...",
    "Verin is worse then the tech support in India",
    "Who are you?!? Where are we? Are you kidnapping me?",
    "The cheese said no!",
    "You didn't hear it from me!"
    "*Ahem",
    "You can't do that right now! The heavens won't allow it!",
    "I do have at least one sensible error message in here, right?",
    "I bet you thought I wouldn't notice :eyes: I always notice :eye: :eye:",
    "What say you now! Vampire King!",
    "Discord senpai... I don't feel too good.",
    "The tininess of his brain dwarfed only by the tininess of his* narrator off",
    "Don't take this the wrong way!",
    "This is why we can't have nice things!",
    "Ah.. um? As you were"
)
