import discord
from dotenv import load_dotenv
import os
import requests
import shutil

from SatanBot import SatanBot

load_dotenv()
ADMIN = os.getenv('ADMIN_ID')

class TestUser:
    def __init__(self, user_id):
        self.user_id = user_id
        self.name = user_id

    async def send(self, message=None, content=None, files=None, suppress_embeds=None, view=None, embed=None):
        print('Message sent to ' + self.user_id + ':')
        if message is not None:
            print('\tcontent: ' + str(message))
        if content is not None:
            print('\tcontent: ' + str(content))
        if files is not None:
            print('\tfiles: ' + str(files))
        if suppress_embeds is not None:
            print('\tsuppress_embeds: ' + str(suppress_embeds))
        if view is not None:
            print('\tview: ' + str(view))
        if embed is not None:
            print('\tembed: ' + str(embed))

async def get_user_by_id(user_id):
    if (user_id.startswith('test')):
        return TestUser(user_id)
    user = SatanBot.client.get_user(user_id)
    if user is None:
        user = await SatanBot.client.fetch_user(user_id)
    return user

async def admin():
    return await get_user_by_id(ADMIN)

async def message_Admin(text, embed = None):
    await (await admin()).send(text, embed=embed)

def download_image(url, path):
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception(f'Download failed with status code {r.status_code}')
    with open(path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
