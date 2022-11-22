import discord

from logfile import log
from SignUp import SignUpButtonView
from SatanBot import SatanBot, State

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
        if message.channel.type == discord.ChannelType.private:
            print('id: ' + str(message.author.id), flush=True)
            async with SatanBot.lock:
                if str(message.author.id) not in SatanBot.satans:
                    if SatanBot.state == State.RECRUITING:
                        log(f'Welcome message sent to {message.author.id}')
                        await message.channel.send('hi', view=SignUpButtonView())
                        SatanBot.satans[str(message.author.id)] = {}
                    else:
                        await message.channel.send('Sorry, sign up period has ended.')

