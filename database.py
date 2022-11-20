#database.py

import asyncio

class State(Enum):
    RECRUITING = 1
    RANDOMIZING = 2
    SETTING = 3
    DELIVERING = 4

class Database:
    _data = {}
    _lock = asyncio.Lock()

    def __init__(self):
        self._data = {
            'satans': {},
            'state': State.RECRUITING,
        }

    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def lock(self):
        return self._lock

