import os
from logfile import log
from SatanBot import SatanBot
from SatanBotClient import SatanBotClient
from dotenv import load_dotenv

load_dotenv()

log('SatanBot restarted')
SatanBot.client = SatanBotClient()
print('Connecting...', flush=True)
SatanBot.client.run(os.getenv('DISCORD_TOKEN'))

