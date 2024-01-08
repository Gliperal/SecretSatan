import discord
import json
import os
import random
import traceback

from DropOut import DropOutButtonView
from logfile import log
from PuzzlePost import PuzzlePost
from SignUp import SignUpButtonView
from SubmitPuzzle import SubmitPuzzleView
from SatanBot import SatanBot, State
from util import admin, message_Admin, get_user_by_id

from send_setter_message import send_setter_message

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

FORMER_PAIRINGS = {
    '628472546546679811': ['458538286416134145'], # Aspartacgus: Andrewsarchus
    '458538286416134145': ['689407844482678830'], # Andrewsarchus: Piatoto
    '689407844482678830': ['319993684362002442'], # Piatoto: dumediat
    '319993684362002442': ['804747286936551515'], # dumediat: filuta
    '804747286936551515': ['774966042412974101'], # filuta: Aaronymous
    '774966042412974101': ['364960653099925505'], # Aaronymous: grkles
    '364960653099925505': ['518935964911927320'], # grkles: Zack Szekely
    '518935964911927320': ['305247910067437569'], # Zack Szekely: RSP (dropped out)
    '305247910067437569': ['820279935238668289'], # RSP (dropped out): samish
    '820279935238668289': ['415592212038942730'], # samish: superrabbit
    '415592212038942730': ['994782206729916467'], # superrabbit: wisteria
    '994782206729916467': ['372882551737417728', '820279935238668289'], # wisteria: Tyrgannus, samish
    '997073167547912295': ['372882551737417728'],                       # Satan's Secretary: Tyrgannus
    '372882551737417728': ['310555686742261769'], # Tyrgannus: Gliperal
    '310555686742261769': ['536089278166335492'], # Gliperal: Astral Sky
    '536089278166335492': ['628472546546679811'], # Astral Sky: Aspartacgus
}

def valid_shuffle(satans):
    n = len(satans)
    for i in range(n):
        satan = satans[i]
        victim = satans[(i + 1) % n]
        if satan['user_id'] in FORMER_PAIRINGS and victim['user_id'] in FORMER_PAIRINGS[satan['user_id']]:
            log(satan['user_id'] + ' already had ' + victim['user_id'])
            return False
    return True

async def randomize(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.RECRUITING:
            await channel.send('Must be in recruiting state to do that')
            return
        SatanBot.state = State.RANDOMIZING
        satans = SatanBot.get_satans()
        while True:
            random.shuffle(satans)
            if valid_shuffle(satans):
                break
        log('Randomization result: ' + str([satan['user_id'] for satan in satans]))
        n = len(satans)
        for i in range(n):
            satan = satans[i]
            victim = satans[(i + 1) % n]
            victim['satan'] = satan['user_id']
            victim['is_victim'] = True
        SatanBot.state = State.SETTING
    for satan in satans:
        await send_setter_message(satan['user_id'], message='Your victim has been assigned! When finished setting their puzzle, send it in this DM exactly how you wish it to appear (including any attached images and files).')

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
            if victim['satan'] is not None:
                satan = await get_user_by_id(victim['satan'])
                await satan.send(reminder_message)
        await message.channel.send('Reminders sent successfully')

async def still_setting(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.SETTING:
            await channel.send('Must be in setting state to do that')
            return
        victims = SatanBot.get_victims()
        ungifted = [v for v in victims if 'gift' not in v]
        ungifter_names = []
        for victim in ungifted:
            if victim['satan'] is not None:
                satan = await get_user_by_id(victim['satan'])
                ungifter_names.append(satan.name)
        await channel.send(', '.join(ungifter_names))

async def message_victim(message, satan_id, text):
    text = text.strip()
    if text == '':
        await message.channel.send('Message cannot be blank')
        return
    async with SatanBot.lock:
        all_victims = SatanBot.get_victims()
        victims = [v for v in all_victims if v['satan'] == satan_id]
        victim = None
        if len(victims) == 0:
            await message.channel.send('No victims found')
            return
        elif len(victims) == 1:
            victim = victims[0]
        else:
            index = text.split()[0]
            if not index.isnumeric():
                victim_list = []
                i = 0
                for i, v in enumerate(victims):
                    victim_list.append(str(i+1) + ' ' + v['preferences']['name'])
                await message.channel.send('Multiple victims assigned:\n' + '\n'.join(victim_list) + '\nSpecify which one with `tell victim [number] [message]`')
                return
            text = text[len(index):].strip()
            if text == '':
                await message.channel.send('Message cannot be blank')
                return
            index = int(index)
            if index < 1 or index > len(victims):
                await message.channel.send('Index out of range')
                return
            victim = victims[index - 1]
        victim_user = await get_user_by_id(victim['user_id'])
        post = PuzzlePost.fromMessage(message)
        post.content = 'Satan says: ' + post.content
        if len(post.content) > 2000:
            await channel.send('Message too long')
            return
        await post.send(victim_user)
        await message.channel.send('Message sent to ' + victim['preferences']['name'])
        log('Victim message sent from ' + satan_id + ' to ' + victim['user_id'] + ': ' + text)

async def message_satan(message, victim_id, text):
    text = text.strip()
    if text == '':
        await channel.send('Message cannot be blank')
        return
    async with SatanBot.lock:
        victim = SatanBot.get_user(victim_id)
        if victim is None:
            await message.channel.send('Not currently participating')
            return
        satan_id = victim['satan']
        if satan_id is None:
            await message.channel.send('No satan found')
            return
        satan_user = await get_user_by_id(satan_id)
        post = PuzzlePost.fromMessage(message)
        post.content = 'Victim ' + victim['preferences']['name'] + ' says: ' + post.content
        if len(post.content) > 2000:
            await message.channel.send('Message too long')
            return
        await post.send(satan_user)
        await message.channel.send('Message sent to Satan')
        log('Satan message sent from ' + victim_id + ' to ' + satan_id + ': ' + text)

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
        if message.content.startswith('tell victim'):
            await message_victim(message, user_id, message.content[11:])
            return
        if message.content.startswith('tell satan'):
            await message_satan(message, user_id, message.content[10:])
            return
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
                await message.channel.send('Signed up for Secret Satan.', view=DropOutButtonView())
            elif SatanBot.state == State.SETTING:
                victims = SatanBot.get_victims_of(user_id)
                if len(victims) == 1:
                    text = 'Your victim: ' + victims[0]['preferences']['name']
                else:
                    text = 'Your victims: ' + ', '.join([victim['preferences']['name'] for victim in victims])
                await message.channel.send(text, view=SubmitPuzzleView(user, victims))
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
