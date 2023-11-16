import asyncio
from copy import deepcopy
from enum import Enum
import json

from send_setter_message import send_setter_message

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
    def get_emergency_satans_sorted():
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
        satan = SatanBot.get_user(user_id)
        if satan is None:
            satan = {'user_id': user_id}
            SatanBot._satans.append(satan)
        satan['preferences'] = preferences
        satan['is_satan'] = True

    @staticmethod
    async def remove_satan(user_id):
        # TODO find a better way to handle all these cyclic imports
        from util import message_Admin, get_user_by_id
        from send_setter_message import send_setter_message
        satan = SatanBot.get_user(user_id)
        satan['is_satan'] = False
        satan['emergency_satan'] = False
        if SatanBot.state == State.SETTING:
            # reassign victims to emergency satans
            victims = SatanBot.get_victims_of(user_id)
            victims = [v for v in victims if 'gift' not in v]
            emergency_satans = SatanBot.get_emergency_satans()
            if (
                len(emergency_satans) == 0 or (
                len(emergency_satans) == 1 and emergency_satans[0] in victims
            )):
                await message_Admin('A satan dropped out and we don\'t have any replacements')
                for victim in victims:
                    victim['satan'] = None
            else:
                for es in emergency_satans:
                    es['tmp_victim_count'] = SatanBot.count_victims_of(es)
                # build replacement satans list based to even out the workload of the emergency satans
                replacements = []
                for i in range(len(victims)):
                    emergency_satans.sort(key=lambda es: es['tmp_victim_count'])
                    replacements.append(emergency_satans[0])
                    emergency_satans[0]['tmp_victim_count'] += 1
                # attempt to assign replacements so that they don't get themselves
                for i in range(len(victims)):
                    if replacements[i] == victims[i]:
                        for j in range(len(victims)):
                            if replacements[i] != victims[j] and replacements[j] != victims[i]:
                                tmp = replacements[i]
                                replacements[i] = replacements[j]
                                replacements[j] = tmp
                                break
                        # if impossible to rearrange to avoid clashes, then pull in a new satan
                        emergency_satans.sort(key=lambda es: es['tmp_victim_count'])
                        replacements[i] = emergency_satans[0]
                        if replacements[i] == victims[i]:
                            replacements[i] = emergency_satans[1]
                        # (no need to re-sort emergency_satans)
                # re-assign
                for i in range(len(victims)):
                    victims[i]['satan'] = replacements[i]['user_id']
                replacement_ids = [r['user_id'] for r in replacements]
                for rid in list(set(replacement_ids)):
                    await send_setter_message(rid, 'You have been assigned new victim(s) due to other satans leaving!')

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
