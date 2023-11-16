import discord
import json
import os
import random
import string
import time

from dotenv import load_dotenv
from util import download_image

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
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=40))
        n = len(self.files)
        local_files = []
        if not os.path.exists(TMP_FOLDER):
            os.mkdir(TMP_FOLDER)
        for i in range(n):
            file = self.files[i]
            path = f'{TMP_FOLDER}/{rand}{i}'
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
            path = f'{TMP_FOLDER}/{rand}{i}'
            try:
                os.remove(path)
            except PermissionError:
                print('failed to remove ' + path + '... ignoring')
