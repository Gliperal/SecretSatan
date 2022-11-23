import discord
import os
from dotenv import load_dotenv

from SatanBot import SatanBot

load_dotenv()
ADMIN = os.getenv('ADMIN_ID')

async def get_user_by_id(user_id):
    user = SatanBot.client.get_user(ADMIN)
    if user is None:
        user = await SatanBot.client.fetch_user(ADMIN)
    return user

async def admin():
    return await get_user_by_id(ADMIN)

async def message_Admin(text, embed = None):
    await (await admin()).send(text, embed=embed)

