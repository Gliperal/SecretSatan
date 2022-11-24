import asyncio
import json
from enum import Enum

BACKUP_FILE = 'bot.json'

class State(str, Enum):
    RECRUITING = 'RECRUITING'
    RANDOMIZING = 'RANDOMIZING'
    SETTING = 'SETTING'
    EMERGENCY = 'EMERGENCY'
    DELIVERING = 'DELIVERING'

class SatanBot():
    client=None
    satans = {}
    victims = {}
    state = State.RECRUITING
    lock = asyncio.Lock()

    @staticmethod
    async def save():
        async with SatanBot.lock:
            victims = SatanBot.victims
            for victim_id in victims:
                if 'gift' in victims[victim_id]:
                    victims[victim_id]['gift'] = victims[victim_id]['gift'].toDict()
            data = {
                'satans': SatanBot.satans,
                'victims': victims,
                'state': SatanBot.state
            }
            with open(BACKUP_FILE, 'w') as f:
                f.write(json.dumps(data))

    @staticmethod
    async def load():
        # Dumb hacky way of doing cyclic dependencies
        from SatanBotClient import PuzzlePost
        async with SatanBot.lock:
            data = None
            with open(BACKUP_FILE, 'r') as f:
                data = json.loads(f.read())
            victims = data['victims']
            for victim_id in victims:
                if 'gift' in victims[victim_id]:
                    victims[victim_id]['gift'] = PuzzlePost.fromDict(victims[victim_id]['gift'])
            SatanBot.satans = data['satans']
            SatanBot.victims = victims
            SatanBot.state = data['state']

