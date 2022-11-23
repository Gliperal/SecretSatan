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
    def __init__(self, message):
        self.content = message.content
        self.files = [
            {'url': attachment.url, 'filename': attachment.filename}
            for attachment in message.attachments
        ]
        self.suppress_embeds = message.flags.suppress_embeds

    def __str__(self):
        data = {
            'content': self.content,
            'files': self.files,
            'suppress_embeds': self.suppress_embeds
        }
        return f'PuzzlePost({json.dumps(data)})'

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
            await channel.send(f'Recruited {len(SatanBot.keys())} satans so far')
        elif SatanBot.state == State.RANDOMIZING:
            await channel.send('Randomizing satans and sending out victims')
        elif SatanBot.state == State.SETTING:
            satan_ids = list(SatanBot.satans.keys())
            gifted = [sid for sid in satan_ids if 'gift' in SatanBot.satans[sid]]
            await channel.send(f'Setting in progress: {len(gifted)}/{len(satan_ids)} gifts completed')
        elif SatanBot.state == State.DELIVERING:
            await channel.send(f'Merry Christmas')
        else:
            await channel.send('I have no idea what it going on')

async def randomize(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.RECRUITING:
            await channel.send('Must be in recruiting state to do that')
            return
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

# TODO Emergency gifting: anyone who doesn't yet have a gift, asign them a new gifter (not themselves)

async def distribute(channel):
    async with SatanBot.lock:
        if SatanBot.state != State.SETTING:
            await channel.send('Must be in setting state to do that')
            return
        for victim_id in SatanBot.satans:
            if 'gift' not in SatanBot.satans[victim_id]:
                await channel.send('Still missing gifts')
                return
        for victim_id in SatanBot.satans:
            victim = await get_user_by_id(victim_id)
            await victim.send('Incoming message from Satan:')
            await SatanBot.satans[victim_id]['gift'].send(victim)

class SatanBotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        #intents.message_content = True
        #intents.members = True
        super().__init__(intents=intents)

    async def setup_hook(self) -> None:
        # why do I need this?
        self.add_view(SignUpButtonView())
        self.add_view(SubmitPuzzleButtonView(None, None))

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
        if message.channel.type == discord.ChannelType.private:
            async with SatanBot.lock:
                if str(message.author.id) not in SatanBot.satans:
                    if SatanBot.state == State.RECRUITING:
                        log(f'Welcome message sent to {message.author.id}')
                        await message.channel.send('', view=SignUpButtonView())
                        SatanBot.satans[str(message.author.id)] = {}
                    else:
                        await message.channel.send('Sorry, sign up period has ended.')
                elif SatanBot.state == State.SETTING:
                    puzzle_post = PuzzlePost(message)
                    satan_id = str(message.author.id)
                    victim_id = SatanBot.satans[satan_id]['victim']
                    await puzzle_post.send(message.channel, SubmitPuzzleButtonView(victim_id, puzzle_post))

