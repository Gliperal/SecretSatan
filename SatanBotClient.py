import discord
import json
import os
import random

from logfile import log
from SignUp import SignUpButtonView
from SubmitPuzzle import SubmitPuzzleButtonView
from SatanBot import SatanBot, State
from util import admin, get_user_by_id, download_image

from dotenv import load_dotenv

load_dotenv()
TMP_FOLDER = os.getenv('TMP_FOLDER')

class PuzzlePost:
    def __init__(self, content, files, suppress_embeds):
        self.content = content
        self.files = files
        self.suppress_embeds = suppress_embeds

    @staticmethod
    def fromMessage(message):
        return PuzzlePost(
            message.content,
            [
                {'url': attachment.url, 'filename': attachment.filename}
                for attachment in message.attachments
            ],
            message.flags.suppress_embeds
        )

    @staticmethod
    def fromDict(data):
        return PuzzlePost(data['content'], data['files'], data['suppress_embeds'])

    def toDict(self):
        return {
            'content': self.content,
            'files': self.files,
            'suppress_embeds': self.suppress_embeds
        }

    def __str__(self):
        return f'PuzzlePost({json.dumps(self.toDict())})'

    async def send(self, channel, view=None):
        # TODO catch failures
        n = len(self.files)
        local_files = []
        if not os.path.exists(TMP_FOLDER):
            os.mkdir(TMP_FOLDER)
        for i in range(n):
            file = self.files[i]
            path = f'{TMP_FOLDER}/{i}'
            if os.path.exists(path):
                os.remove(path)
            download_image(file['url'], path)
            local_files.append(discord.File(path, filename=file['filename']))
        await channel.send(
            content=self.content,
            files=local_files,
            suppress_embeds=self.suppress_embeds,
            view=view
        )
        for i in range(n):
            os.remove(f'{TMP_FOLDER}/{i}')

async def status(channel):
    async with SatanBot.lock:
        if SatanBot.state == State.RECRUITING:
            await channel.send(f'Recruited {len(SatanBot.victims.keys())} satans so far')
        elif SatanBot.state == State.RANDOMIZING:
            await channel.send('Randomizing satans and sending out victims')
        elif SatanBot.state == State.SETTING or SatanBot.state == State.EMERGENCY:
            victim_ids = list(SatanBot.victims.keys())
            gifted = [sid for sid in victim_ids if 'gift' in SatanBot.victims[sid]]
            await channel.send(f'Setting in progress: {len(gifted)}/{len(victim_ids)} gifts completed')
        elif SatanBot.state == State.DELIVERING:
            await channel.send(f'Merry Christmas')
        else:
            await channel.send('I have no idea what it going on')

async def send_setter_message(satan_id):
    async with SatanBot.lock:
        victim_id = SatanBot.satans[satan_id]['victim']
        satan = await get_user_by_id(satan_id)
        victim = await get_user_by_id(victim_id)
        preferences = SatanBot.victims[victim_id]['preferences']
        embed = discord.Embed(description=f"Name: {preferences['name']}"+ \
            f"\n\nAbout Them: {preferences['about_you']}"+ \
            f"\n\nPuzzles They Enjoy: {preferences['puzzles_enjoyed']}"+ \
            f"\n\nFavorite Puzzle Types: {preferences['favorite_puzzle_types']}"+ \
            f"\n\nAnything Else: {preferences['anything_else']}")
        await satan.send('Your victim has been assigned! When finished setting their puzzle, send it in this DM exactly how you wish it to appear (including any attached images and files).', embed=embed)

async def randomize(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.RECRUITING:
            await channel.send('Must be in recruiting state to do that')
            return
        SatanBot.state = State.RANDOMIZING
        satan_ids = list(SatanBot.victims.keys())
        random.shuffle(satan_ids)
        log(f'Randomization result: {satan_ids}')
        n = len(satan_ids)
        for i in range(n):
            satan_id = satan_ids[i]
            victim_id = satan_ids[(i + 1) % n]
            SatanBot.satans[satan_id] = {'victim': victim_id}
        SatanBot.state = State.SETTING
    for satan_id in satan_ids:
        await send_setter_message(satan_id)

async def emergency(channel, emergency_setters):
    setters = json.loads(emergency_setters)
    async with SatanBot.lock:
        if SatanBot.state != State.SETTING:
            await channel.send('Must be in setting state to do that')
            return
        victim_ids = list(SatanBot.victims.keys())
        ungifted = [vid for vid in victim_ids if 'gift' not in SatanBot.victims[vid]]
    # TODO Emergency gifting: anyone who doesn't yet have a gift, asign them a new gifter (not themselves)

async def distribute(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.SETTING and SatanBot.state != State.EMERGENCY:
            await channel.send('Must be in setting state to do that')
            return
        for victim_id in SatanBot.victims:
            if 'gift' not in SatanBot.victims[victim_id]:
                await channel.send('Still missing gifts')
                return
        SatanBot.state = State.DELIVERING
        for victim_id in SatanBot.victims:
            victim = await get_user_by_id(victim_id)
            await victim.send('Incoming message from Satan:')
            await SatanBot.victims[victim_id]['gift'].send(victim)

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
        if message.channel.type == discord.ChannelType.private:
            async with SatanBot.lock:
                if str(message.author.id) not in SatanBot.victims:
                    if SatanBot.state == State.RECRUITING:
                        #SatanBot.victims[str(message.author.id)] = {}
                        log(f'Welcome message sent to {message.author.id}')
                        await message.channel.send('', view=SignUpButtonView())
                    else:
                        await message.channel.send('Sorry, sign up period has ended.')
                elif SatanBot.state == State.SETTING:
                    puzzle_post = PuzzlePost.fromMessage(message)
                    satan_id = str(message.author.id)
                    victim_id = SatanBot.satans[satan_id]['victim']
                    await puzzle_post.send(message.channel, SubmitPuzzleButtonView(victim_id, puzzle_post))

