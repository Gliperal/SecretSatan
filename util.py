import discord
from dotenv import load_dotenv

load_dotenv()
ADMIN = os.getenv('DEVELOPER_ID')

def admin():
    await client.get_user(ADMIN)

def message_Admin(client, text, embed = None):
    await client.get_user(ADMIN).send(text, embed=embed)

