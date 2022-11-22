import discord
import os
from dotenv import load_dotenv

from SatanBot import SatanBot

load_dotenv()
ADMIN = os.getenv('DEVELOPER_ID')

async def admin():
    await SatanBot.client.get_user(ADMIN)

async def get_user_by_id(user_id):
    await SatanBot.client.get_user(user_id)

async def message_Admin(text, embed = None):
    await SatanBot.client.get_user(ADMIN).send(text, embed=embed)

