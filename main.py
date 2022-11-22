import os
from SatanBot import SatanBot
from SatanBotClient import SatanBotClient
from dotenv import load_dotenv

load_dotenv()

SatanBot.client = SatanBotClient()
print('Connecting...', flush=True)
SatanBot.client.run(os.getenv('DISCORD_TOKEN'))

