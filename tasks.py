import requests
from invoke import task

DISCORD_API_URL = 'https://discord.com/api/v10/applications/<YOUR_APPLICATION_ID>/guilds/<YOUR_GUILD_ID>/commands'
HEADERS = {
    'Authorization': 'Bot <YOUR BOT TOKEN, KEEP SECURE>'
}

COMMANDS = [
    {
        'name': 'start',
        'type': 1,
        'description': 'Start minecraft server',
        'options': []
    },
    {
        'name': 'stop',
        'type': 1,
        'description': 'Stop minecraft server',
        'options': []
    },
    {
        'name': 'ip',
        'type': 1,
        'description': 'Get minecraft server IP address',
        'options': []
    },
]


@task
def register_commands(c):
    for command in COMMANDS:
        r = requests.post(DISCORD_API_URL, headers=HEADERS, json=command)

        print(r)


@task
def list_guild_commands(c):
    r = requests.get(DISCORD_API_URL, headers=HEADERS)

    print(r.json())


@task
def delete_guild_command(c, command_id):
    r = requests.delete('{0}/{1}'.format(DISCORD_API_URL, command_id), headers=HEADERS)

    print(r)
