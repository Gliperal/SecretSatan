import os

from discord.ext import commands
import discord
from dotenv import load_dotenv
from database import Database, State

load_dotenv()

async def send_welcome_message(channel):
    await channel.send('hi')

class SatanBotClient(discord.Client):
    async def on_ready(self):
        print(f'{self.user} connected.', flush=True)

    async def on_message(self, message):
        # Ignore own messages
        if message.author == client.user:
            return
        if message.channel.type == discord.ChannelType.private:
            async with database.lock():
                data = database.get_data()
                if message.author.name not in data['satans']:
                    if data['state'] == State.RECRUITING:
                        send_welcome_message(message.channel)
                        # When form comes back, add user to satans
                    else:
                        await message.channel.send('Sorry, recruitment period expired.')
                database.set_data(data)

class SatanBot():
    client = SatanBotClient()
    satans = {}
    #lock =

print('Connecting...', flush=True)
SatanBot.client.run(os.getenv('DISCORD_TOKEN'))

