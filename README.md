# REQUIEM
###Free, Powerful, Flexible
***
#### About Requiem
Requiem is a specially crafted discord bot built to provide the largest number of tools and resources to help the
politics and war community in a convenient and easy to use package. Requiem has been rewritten from the ground up for
stability, ease of use, and readability, so those who wish to modify Requiem for their own purposes can do so easily.
Requiem is, always has been, and always will be completely free for everyone. No walls or barriers will ever be put up
to single out any individual or alliance. If you're concerned about security and privacy on your discord server, know
that Requiem doesn't need access to messages since it works entirely off of discords interactions api (slash commands)
which does not require the messages intent. Failing that, you're more than welcome to self-host Requiem which has been
made easier than ever thanks to the bot being capable of running on a sqlite database which requires no additional
applications be installed besides python. If you need help self-hosting, wish to submit a bug report, or request a new
feature, feel free to join Requiem's [discord server](https://discord.gg/uTXdx7J).
***
#### Adding Requiem to your guild
Adding Requiem to your server is easy. Simply follow this [invite link](https://discord.com/oauth2/authorize?client_id=406643604019347456&scope=bot).
Select the desired server from the dropdown list and click authorize. Note how there are no permission toggles on the 
interface. Requiem requires **NO** permissions to perform any of its basic operations or politics and war operations.
***
#### Self-hosting Requiem
Self-hosting Requiem requires a bit more from you. To start, you'll need to create a bot application with discord.
Follow [this tutorial](https://tutorials.discordcoding.academy/starting/making-the-bot.html) to create your bot
application. Note that you **do not** need any of the privileged intents for Requiem to function.

#### Windows

* Step 1 - Install Required Applications
  * For basic functionality, Requiem only requires [Python 3.10](https://python.org) making sure to tick the 
  **add python to path** box
  * If you intend on providing Requiem to more than just a handful of servers, it is advised you also get [Postgresql](https://postgresql.org/)
  * If you are new to using Postgresql, you'll want to make a note of the password you enter during its install

* Step 2 - Download Requiem
  * To download Requiem, click the green **Code** button above the directory list and click **Download ZIP**
  * Once the ZIP folder is downloaded, you'll want to extract the folder
  * Alternatively, if you have [git](https://git-scm.com/downloads) downloaded, you can run 
  **git clone https://github.com/GodEmpressVerin/requiem.git** in command prompt, powershell, or any other terminal

* Step 3 - Install Required Packages
  * More installs? Yes, but we're almost done. Within command prompt, powershell, or terminal, you'll want to change
  directories into the downloaded Requiem folder
  * Once there, run the command **pip install -r requirements.txt**
  
* Step 4 - Create Credentials File
  * Within the installed Requiem folder, you'll find yet another Requiem folder. Here, you will create a file named
  **credentials.yaml**
  * This file is important, it contains all your basic configuration details that aren't modifiable post launch
  * Below you will find a list of available fields for the file as well as a template
  * If you've installed Postgresql and wish to use its default configuration, make sure you add postgres_password to the
  credentials.yaml file with the password you set during install

* Step 5 - Run Requiem
  * Lastly, within command prompt, powershell, or terminal, change directories into the previously mentioned nested
  Requiem folder. Then run the command **python __main__.py**
  * Requiem should now be starting up. Note that it may take a while to process commands (add the commands to discord)
  if you have not specified enabled_guilds in the credentials.yaml file

#### Linux

* Steps for Linux coming soon...

Should you encounter any problems getting Requiem running, or need help getting the postgresql database setup, please
ask for help in Requiem's [discord server](https://discord.gg/uTXdx7J)
