import discord
import random

from logfile import log
from SignUp import SignUpButtonView
from SatanBot import SatanBot, State
from util import admin, get_user_by_id

async def status(channel):
    async with SatanBot.lock:
        if SatanBot.state == RECRUITING:
            channel.send(f'Recruited {len(SatanBot.keys())} satans so far')
        elif SatanBot.state == RANDOMIZING:
            channel.send('Randomizing satans and sending out victims')
        elif SatanBot.state == SETTING:
            channel.send(f'Setting in progress') # TODO how many completed ?
        elif SatanBot.state == DELIVERING:
            channel.send(f'Merry Christmas')
        else:
            channel.send('I have no idea what it going on')

async def randomize(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.RECRUITING:
            await message.channel.send('Must be in recruiting state to do that')
        else:
            SatanBot.state = State.RANDOMIZING
            satan_ids = list(SatanBot.satans.keys())
            random.shuffle(satan_ids)
            log(f'Randomization result: {satan_ids}')
            n = len(satan_ids)
            for i in range(n):
                satan_id = satan_ids[i]
                victim_id = satan_ids[(i + 1) % n]
                SatanBot.satans[satan_id]['victim'] = victim_id
                # TODO try catch report errors
                satan = await get_user_by_id(satan_id)
                victim = await get_user_by_id(victim_id)
                preferences = SatanBot.satans[victim_id]['preferences']
                embed = discord.Embed(description=f"Name: {preferences['name']}"+ \
                    f"\n\nAbout Them: {preferences['about_you']}"+ \
                    f"\n\nPuzzles They Enjoy: {preferences['puzzles_enjoyed']}"+ \
                    f"\n\nFavorite Puzzle Types: {preferences['favorite_puzzle_types']}"+ \
                    f"\n\nAnything Else: {preferences['anything_else']}")
                await satan.send('Your victim has been assigned! When finished setting their puzzle, send it in this DM exactly how you wish it to appear (including any attached images and files).', embed=embed)
                print(SatanBot.satans, flush=True)
            SatanBot.state = State.SETTING

async def distribute(channel):
    pass

class SatanBotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        #intents.message_content = True
        #intents.members = True
        super().__init__(intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(SignUpButtonView())

    async def on_ready(self):
        print(f'{self.user} connected.', flush=True)

    async def on_message(self, message):
        # Ignore own messages
        if message.author == self.user:
            return
        if message.author == await admin():
            if message.content == 'status':
                await status(message.channel)
                return
            if message.content == 'begin randomization':
                await randomize(message.channel)
                return
            if message.content == 'begin distribution':
                await distribute()
                return
        if message.channel.type == discord.ChannelType.private:
            async with SatanBot.lock:
                if str(message.author.id) not in SatanBot.satans:
                    if SatanBot.state == State.RECRUITING:
                        log(f'Welcome message sent to {message.author.id}')
                        await message.channel.send('hi', view=SignUpButtonView())
                        SatanBot.satans[str(message.author.id)] = {}
                    else:
                        await message.channel.send('Sorry, sign up period has ended.')
                elif SatanBot.state == State.SETTING:
                    satan_id = str(message.author.id)
                    victim_id = SatanBot.satans[satan_id]
                    # TODO Copy message back exactly as sent "is this how you want it? if so, click the button"
                    # If all good, store the message + images + embeds + other files in the database and send message "recorded, if you need to change anything before Dec 18, simply resend the message"

