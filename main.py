from discord import Message

import mutiny
from bot import client, start


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message: Message):
    await client.process_commands(message)


mutiny.setup(client)

start()
