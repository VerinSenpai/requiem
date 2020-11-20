# Requiem Project

### Discord.py
This is the [DPY](https://discordpy.readthedocs.io/en/latest/) build of Requiem. Requiem's hikari and dpy builds are
being built to be as identical as possible internally and indiscernible by the end user. This is being done for
consistencies sake and ease of development.

### Description
Requiem project aims to provide a free and open source nation sim utility discord bot. Requiem is, has always been, and
always will be free to use for anybody who wishes to do so. Requiem is currently geared towards the [Politics and War](https://politicsandwar.com/)
with plans to also support A&O when it releases.

### Self Hosting
Requiem requires [Python 3.8+](https://www.python.org/). Requiem relies on a database for a lot of functionality. For
this database, we've opted to use sql and tortoise. Note that if you only plan to service your own server and maybe a
few friends servers, you don't need to install postgresql. However, if you do plan on providing Requiem to a large
number of guilds, you will want to install a [postgres server](https://www.postgresql.org/).

You will also need to setup a bot account in the [discord developer portal](https://discord.com/developers/applications).
Instructions for how to do so can be found on [dcacademy](https://dcacademy.gitlab.io/tutorials/starting/making-the-bot.html).
Do not give your token to anybody. These tokens are powerful. Requiem is not liable for any damages that occur as a
result of you negligently leaking your bot token.

Enter into the console. Any console that can access python will do. I personally recommend [Terminus](https://eugeny.github.io/terminus/).
Change into the bots directory and run `pip install -r requirements.txt`. Assuming python is in path (windows) or pip is
installed (linux) python should install the bots requirements. If you encounter an error saying pip is not a recognized
command, you should make sure python is in path (windows) or that pip is installed (linux).

Create a file called `config.yaml` in the bots folder. The following is a list of arguments you can specify here for
additional functionality.
    
    discord_token     | REQUIRED | TEXT |                       | the token to use for connection to discord
    default_prefix    | OPTIONAL | TEXT | defaults to r!        | the prefix to use for detecting commands
    owner_ids         | OPTIONAL | LIST | defaults to []        | users who should have access to owner commands
    show_statuses     | OPTIONAL | BOOL | defaults to True      | sets whether requiem should show statuses
    prefix_on_mention | OPTIONAL | BOOL | defaults to True      | sets whether requiem should state the current prefix when mentioned.
    report_errors     | OPTIONAL | BOOL | defaults to True      | sets whether requiem should report errors to the owners
    postgres_host     | OPTIONAL | TEXT | defaults to localhost | the host to be connected to for postgres
    postgres_port     | OPTIONAL | INT  | defaults to 5432      | the port to be connected to for postgres
    postgres_database | OPTIONAL | TEXT | defaults to postgres  | the database to be connected to for postgres
    postgres_user     | OPTIONAL | TEXT | defaults to postgres  | the user to be used for logging into for postgres
    postgres_password | OPTIONAL | TEXT | defaults to None      | the password to be used for logging into postgres

You do not need to specify all of the values above, only the ones you desire to set and that are required. For those
that you do not set, the default will be used.