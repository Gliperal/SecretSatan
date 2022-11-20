import os

from discord.ext import commands
import discord
from dotenv import load_dotenv
from database import Database, State

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

database = Database()

@client.event
async def on_ready():
    print(f'{client.user} connected.', flush=True)

async def send_welcome_message(channel):
    await message.channel.send('hi')

@client.event
async def on_message(message):
    # Ignore own messages
    if message.author == client.user:
        return
    if message.channel.type == discord.ChannelType.private:
        async with database.lock():
            data = database.get_data()
            if message.author.name not in data['satans']:
                if data['state'] == State.RECRUITING:
                    pass # Send welcome message and add user
                else:
                    await message.channel.send('Sorry, recruitment period expired.')
            database.set_data(data)

print('Connecting...', flush=True)
client.run(TOKEN)

