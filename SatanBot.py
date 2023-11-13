import asyncio
from copy import deepcopy
from enum import Enum
import json

BACKUP_FILE = 'bot.json'

class State(str, Enum):
    RECRUITING = 'RECRUITING'
    RANDOMIZING = 'RANDOMIZING'
    SETTING = 'SETTING'
    DELIVERING = 'DELIVERING'

class SatanBot():
    client=None
    _satans = []
    state = State.RECRUITING
    lock = asyncio.Lock()

    @staticmethod
    def get_satans():
        return [x for x in SatanBot._satans if 'is_satan' in x and x['is_satan'] == True]

    @staticmethod
    def get_victims():
        return [x for x in SatanBot._satans if 'is_victim' in x and x['is_victim'] == True]

    @staticmethod
    def get_emergency_satans():
        return [x for x in SatanBot._satans if 'emergency_satan' in x and x['emergency_satan'] == True]

    @staticmethod
    def get_underworked_emergency_satans():
        emergency_satans = SatanBot.get_emergency_satans()
        underworked = []
        min_work = 999999
        for satan in emergency_satans:
            count = SatanBot.count_victims_of(satan['user_id'])
            if count < min_work:
                min_work = count
                underworked = [satan]
            elif count == min_work:
                underworked.append(satan)
        return underworked

    @staticmethod
    def get_user(user_id):
        matches = [x for x in SatanBot._satans if 'user_id' in x and x['user_id'] == user_id]
        if len(matches) > 0:
            return matches[0]
        return None

    @staticmethod
    def get_victims_of(user_id):
        return [x for x in SatanBot._satans if 'satan' in x and x['satan'] == user_id]

    @staticmethod
    def count_victims_of(user_id):
        return len(SatanBot.get_victims_of(user_id))

    @staticmethod
    def add_satan(user_id, preferences):
        SatanBot._satans.append({
            'user_id': user_id,
            'preferences': preferences,
            'is_satan': True,
            'is_victim': True,
        })

    @staticmethod
    def add_emergency_satan(user_id):
        SatanBot._satans.append({
            'user_id': user_id,
            'is_satan': True,
            'emergency_satan': True,
        })

    @staticmethod
    async def save():
        async with SatanBot.lock:
            satans = deepcopy(SatanBot._satans)
            for satan in satans:
                if 'gift' in satan:
                    satan['gift'] = satan['gift'].toDict()
            data = {
                'satans': satans,
                'state': SatanBot.state
            }
            with open(BACKUP_FILE, 'w') as f:
                f.write(json.dumps(data))

    @staticmethod
    async def load():
        # Dumb hacky way of doing cyclic dependencies
        from PuzzlePost import PuzzlePost
        async with SatanBot.lock:
            data = None
            with open(BACKUP_FILE, 'r') as f:
                data = json.loads(f.read())
            for satan in data['satans']:
                if 'gift' in satan:
                    satan['gift'] = PuzzlePost.fromDict(satan['gift'])
            SatanBot._satans = data['satans']
            SatanBot.state = data['state']
