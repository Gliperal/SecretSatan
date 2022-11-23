import asyncio
from enum import Enum

class State(Enum):
    RECRUITING = 1
    RANDOMIZING = 2
    SETTING = 3
    DELIVERING = 4

class SatanBot():
    #client = SatanBotClient()
    client=None
    #satans = {}
    #satans = {'310555686742261769': {'preferences': {'name': 'Gliperal', 'realname': '', 'about_you': 'A', 'puzzles_enjoyed': 'B', 'favorite_puzzle_types': 'C', 'anything_else': 'D'}}}
    satans = {'310555686742261769': {'preferences': {'name': 'Gliperal', 'realname': '', 'about_you': 'A', 'puzzles_enjoyed': 'B', 'favorite_puzzle_types': 'C', 'anything_else': 'D'}, 'victim': '310555686742261769'}}
    #state = State.RECRUITING
    state = State.SETTING
    lock = asyncio.Lock()

