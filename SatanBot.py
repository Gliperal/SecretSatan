import asyncio
from enum import Enum

class State(Enum):
    RECRUITING = 1
    RANDOMIZING = 2
    SETTING = 3
    DELIVERING = 4

class SatanBot():
    #client = SatanBotClient(intents=discord.Intents.default())
    #client = SatanBotClient()
    client=None
    satans = {}
    state = State.RECRUITING
    lock = asyncio.Lock()

