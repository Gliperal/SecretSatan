import discord
import json
import os
import random
import traceback

from logfile import log
from PuzzlePost import PuzzlePost
from SignUp import SignUpButtonView
from SubmitPuzzle import SubmitPuzzleView
from SatanBot import SatanBot, State
from util import admin, message_Admin, get_user_by_id, download_image

from dotenv import load_dotenv

load_dotenv()
TMP_FOLDER = os.getenv('TMP_FOLDER')

async def status(channel):
    async with SatanBot.lock:
        if SatanBot.state == State.RECRUITING:
            await channel.send(f'Recruited {len(SatanBot.get_satans())} satans so far')
        elif SatanBot.state == State.RANDOMIZING:
            await channel.send('Randomizing satans and sending out victims')
        elif SatanBot.state == State.SETTING:
            victims = SatanBot.get_victims()
            gifted = [v for v in victims if 'gift' in v]
            await channel.send(f'Setting in progress: {len(gifted)}/{len(victims)} gifts completed')
        elif SatanBot.state == State.DELIVERING:
            await channel.send(f'Merry Christmas')
        else:
            await channel.send('I have no idea what it going on')

async def send_setter_message(satan_id, use_embed=True):
    pass
#TODO
#    async with SatanBot.lock:
#        victim_id = SatanBot.satans[satan_id]['victim']
#        satan = await get_user_by_id(satan_id)
#        victim = await get_user_by_id(victim_id)
#        preferences = SatanBot.victims[victim_id]['preferences']
#        embed_content = f"Name: {preferences['name']}"+ \
#            f"\n\nAbout Them: {preferences['about_you']}"+ \
#            f"\n\nPuzzles They Enjoy: {preferences['puzzles_enjoyed']}"+ \
#            f"\n\nFavorite Puzzle Types: {preferences['favorite_puzzle_types']}"+ \
#            f"\n\nAnything Else: {preferences['anything_else']}"
#        if use_embed:
#            embed = discord.Embed(description=embed_content)
#            await satan.send('Your victim has been assigned! When finished setting their puzzle, send it in this DM exactly how you wish it to appear (including any attached images and files).', embed=embed)
#        else:
#            await satan.send('Your victim has been assigned! When finished setting their puzzle, send it in this DM exactly how you wish it to appear (including any attached images and files)\n\n' + embed_content)

async def randomize(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.RECRUITING:
            await channel.send('Must be in recruiting state to do that')
            return
        SatanBot.state = State.RANDOMIZING
        satans = SatanBot.get_satans()
        random.shuffle(satans)
        log('Randomization result: ' + [satan['user_id'] for satan in satans])
        n = len(satans)
        for i in range(n):
            satan = satans[i]
            victim = satans[(i + 1) % n]
            victim['satan'] = satan['user_id']
            victim['is_victim'] = True
        SatanBot.state = State.SETTING
    for satan_id in satan_ids:
        await send_setter_message(satan_id)

#async def emergency(channel, emergency_setters):
#    setters = json.loads(emergency_setters)
#    for i in range(len(setters)):
#        # make sure each id is a valid id
#        setters[i] = str(setters[i])
#        await get_user_by_id(setters[i])
#    async with SatanBot.lock:
#        if SatanBot.state != State.SETTING:
#            await channel.send('Must be in setting state to do that')
#            return
#        victim_ids = list(SatanBot.victims.keys())
#        ungifted = [vid for vid in victim_ids if 'gift' not in SatanBot.victims[vid]]
#        n = len(ungifted)
#        if len(setters) > n:
#            setters = setters[:n]
#        ungifted_nonsetters = [s for s in ungifted if s not in setters]
#        ungifted_setters = [s for s in setters if s in ungifted]
#        gifted_setters = [s for s in setters if s not in ungifted]
#        order = list(range(n))
#        random.shuffle(order)
#        victims = ungifted_setters + ungifted_nonsetters
#        satans = ungifted_setters + gifted_setters
#        log(f'Emergency setter assignments:\n\tvictims={victims}\n\tsatans={satans}\n\torder={order}\n')
#        for i in range(n):
#            satan_id = satans[order[i]]
#            victim_id = victims[order[(i + 1) % n]]
#            SatanBot.satans[satan_id] = {'victim': victim_id}
#        for satan_id in satans:
#            await send_setter_message(satan_id)

async def distribute(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.SETTING:
            await channel.send('Must be in setting state to do that')
            return
        for victim in SatanBot.get_victims():
            if 'gift' not in victim:
                await channel.send('Still missing gifts')
                return
        SatanBot.state = State.DELIVERING
        for victim in SatanBot.get_victims():
            victim_user = await get_user_by_id(victim['user_id'])
            await victim_user.send('Incoming message from Satan:')
            await victim['gift'].send(victim_user)

async def reminder(channel, reminder_message):
    async with SatanBot.lock:
        if SatanBot.state != State.SETTING:
            await channel.send('Must be in setting state to do that')
            return
        if reminder_message == '':
            await message.channel.send('Missing reminder message')
            return
        victims = SatanBot.get_victims()
        ungifted = [v for v in victims if 'gift' not in v]
        for victim in ungifted:
            satan = await get_user_by_id(victim['satan'])
            await satan.send(reminder_message)

async def still_setting(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.SETTING:
            await channel.send('Must be in setting state to do that')
            return
        victims = SatanBot.get_victims()
        ungifted = [v for v in victims if 'gift' not in v]
        ungifter_names = []
        for victim in ungifted:
            satan = await get_user_by_id(victim['satan'])
            ungifter_names.append(satan.name)
        await channel.send(', '.join(ungifter_names))

async def handle_message(message):
    if message.author == await admin():
        if message.content == 'status':
            await status(message.channel)
            return
        if message.content == 'begin randomization':
            await randomize(message.channel)
            return
        if message.content == 'begin distribution':
            await distribute(message.channel)
            return
        if message.content.startswith('emergency'):
            await emergency(message.channel, message.content[9:])
            return
        if message.content == 'save':
            await SatanBot.save()
            return
        if message.content == 'load':
            await SatanBot.load()
            return
        if message.content.startswith('resend_raw'):
            satan_id = message.content[10:].strip()
            await send_setter_message(satan_id, False)
            await message.channel.send(f'Resent victim message to {satan_id} as raw text')
            return
        elif message.content.startswith('resend'):
            satan_id = message.content[6:].strip()
            await send_setter_message(satan_id)
            await message.channel.send('Resent victim message to ' + satan_id)
            return
        if message.content == 'still setting':
            await still_setting(message.channel)
            return
        if message.content.startswith('reminder'):
            await reminder(message.channel, message.content[8:].strip())
            return
    if message.channel.type == discord.ChannelType.private:
        user_id = str(message.author.id)
        async with SatanBot.lock:
            user = SatanBot.get_user(user_id)
            if user is None:
                if SatanBot.state == State.RECRUITING:
                    log(f'Welcome message sent to {message.author.id}')
                    await message.channel.send('', view=SignUpButtonView())
                else:
                    await message.channel.send('Sorry, sign up period has ended.')
            elif 'is_satan' not in user or not user['is_satan']:
                if SatanBot.state == State.RECRUITING:
                    await message.channel.send('You are not currently participating in Secret Satan.', view=SignUpButtonView())
                else:
                    await message.channel.send('You are not currently participating in Secret Satan.')
            elif SatanBot.state == State.RECRUITING or SatanBot.state == State.RANDOMIZING:
                await message.channel.send('Signed up for Secret Satan.', view=DropOutButtonView)
            elif SatanBot.state == State.SETTING:
                victims = SatanBot.get_victims_of(user_id)
                if len(victims) == 1:
                    text = 'Your victim: ' + victims[0]['preferences']['name']
                else:
                    text = 'Your victims: ' + ', '.join([victim['preferences']['name'] for victim in victims])
                await message.channel.send(text, SubmitView(user, victims))
#                puzzle_post = PuzzlePost.fromMessage(message)
#                satan_id = str(message.author.id)
#                victim_id = SatanBot.satans[satan_id]['victim']
#                await puzzle_post.send(message.channel, SubmitPuzzleButtonView(victim_id, puzzle_post))
            elif SatanBot.state == State.DELIVERING:
                await message.channel.send('Merry Christmas!')

class SatanBotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        #intents.message_content = True
        #intents.members = True
        super().__init__(intents=intents)

    async def setup_hook(self) -> None:
        # why do I need this?
        pass
        #self.add_view(SignUpButtonView())
        #self.add_view(SubmitPuzzleButtonView(None, None))

    async def on_ready(self):
        print(f'{self.user} connected.', flush=True)

    async def on_message(self, message):
        # Ignore own messages
        if message.author == self.user:
            return
        try:
            await handle_message(message)
        except:
            error_details = f'User: {message.author}\n\n' + \
                f'Message: {message.content}\n\n' + \
                f'{traceback.format_exc()}'
            await message_Admin('Error in message handling', embed=discord.Embed(description=error_details))
