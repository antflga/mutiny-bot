from discord.ext import commands

client = commands.Bot(command_prefix="!", pm_help=True)


def start():
    with open("token", "r") as token:
        data = token.readlines().pop()
        client.run(data, reconnect=True)
