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
    '774966042412974101': ['364960653099925505', '354736491504861184'], # Aaronymous: grkles, damasosos92
    '210554178538438656': ['689566090325786692', '742434404466557002'], # agent2896: thebookwyrms, maizegator
    '628472546546679811': ['458538286416134145', '774966042412974101'], # Aspartacgus: Andrewsarchus, Aaronymous
    '536089278166335492': ['458538286416134145'], # astral.sky: .andrewsarchus
    '458538286416134145': ['689407844482678830', '597445918752636948', '151134789557026817'], # Andrewsarchus: Piatoto, naomatosis, nordy123
    '536089278166335492': ['628472546546679811'], # Astral Sky: Aspartacgus
    '261725593417023499': ['721426464829997127', '458538286416134145'], # ben_karcher: yttrio, Aaronymous
    '407667501267288066': ['689566090325786692'], # Chad2003: thebookwyrms
    '994277013630242816': ['1000153681104207955', '689407844482678830'], # christounet: majorprofanity, Piatoto
    '741712587304992809': ['354736491504861184', '804747286936551515'], # clover: damasosos92, filuta
    '354736491504861184': ['842483011664740372', '814965184438337618'], # damasosos92: jwsinclair, yura_chameleon
    '256465224050147339': ['994277013630242816'], # davmillar: christounet
    '319993684362002442': ['804747286936551515', '536089278166335492'], # dumediat: filuta, astral.sky
    '994782206729916467': ['372882551737417728', '820279935238668289', '862793701603803136'], # fallenprincess (wisteria): Tyrgannus, samish, fjam
    '804747286936551515': ['774966042412974101', '719685532862644258'], # filuta: Aaronymous, SamuPiano
    '862793701603803136': ['310555686742261769', '172619083127193601'], # fjam: gliperal, tesseralis
    '310555686742261769': ['536089278166335492', '628472546546679811', '804747286936551515'], # Gliperal: Astral Sky, Aspartagcus, filuta
    '281853454044102656': ['863331648786268160', '994277013630242816'], # going2killu: microstudy, christounet
    '864099575669456917': ['319993684362002442'], # goodcity_: dumediat
    '364960653099925505': ['518935964911927320'], # grkles: Zack Szekely
    '842483011664740372': ['224375346122719232', '820279935238668289'], # jwsinclair: kaysakado, samish
    '224375346122719232': ['689407844482678830'], # kaysakado: piatato
    '742434404466557002': ['823382333901635615', '721426464829997127'], # maizegator: shintarofh, yttrio
    '1000153681104207955': ['150708089560104961'], # majorprofanity: niverio
    '863331648786268160': ['151134789557026817'], # microstudy: nordy123
    '276829645956055041': ['804747286936551515'], # mormagli: filuta
    '597445918752636948': ['261725593417023499'], # naomatosis: ben_karcher
    '150708089560104961': ['415592212038942730'], # niverio: superrabbit
    '151134789557026817': ['256465224050147339', '281853454044102656'], # nordy123: davmillar, going2killu
    '693755038480465921': ['994782206729916467'], # paletron: fallenprincess
    '689407844482678830': ['319993684362002442', '210554178538438656', '862793701603803136'], # Piatoto: dumediat, agent2896, fjam
    '799265424394551346': ['689407844482678830'], # PrimeWeasel: Piatoto
    '305247910067437569': ['820279935238668289'], # RSP (dropped out): samish
    '820279935238668289': ['415592212038942730', '741712587304992809'], # samish: superrabbit, clover
    '719685532862644258': ['407667501267288066'], # SamuPiano: Chad2003
    '823382333901635615': ['742434404466557002', '721426464829997127'], # shintarofh: maizegator, yttrio
    '415592212038942730': ['994782206729916467', '172619083127193601'], # superrabbit: fallenprincess, tesseralis
    '172619083127193601': ['814965184438337618', '842483011664740372'], # tesseralis: yura_chameleon, jwsinclair
    '689566090325786692': ['864099575669456917', '210554178538438656'], # thebookwyrms: goodcity_, agent2896
    '372882551737417728': ['310555686742261769'], # Tyrgannus: Gliperal
    '721426464829997127': ['281853454044102656', '261725593417023499'], # yttrio: going2killu, ben_karcher
    '814965184438337618': ['693755038480465921', '276829645956055041'], # yura_chameleon: paletron, mormagli
    '518935964911927320': ['305247910067437569'], # Zack Szekely: RSP (dropped out)
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
            await channel.send('Missing reminder message')
            return
        victims = SatanBot.get_victims()
        ungifted = [v for v in victims if 'gift' not in v]
        for victim in ungifted:
            if victim['satan'] is not None:
                satan = await get_user_by_id(victim['satan'])
                await satan.send(reminder_message)
        await channel.send('Reminders sent successfully')

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
            await message.channel.send('Message too long')
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
