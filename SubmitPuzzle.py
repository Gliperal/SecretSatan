import discord

from logfile import log
from SatanBot import SatanBot

class SubmitPuzzleButtonView(discord.ui.View):
    def __init__(self, victim_id, puzzle_post):
        super().__init__(timeout=None)
        self.victim_id = victim_id
        self.puzzle_post = puzzle_post

    @discord.ui.button(label='Click here if you\'re happy with the way this looks', style=discord.ButtonStyle.green, custom_id='persistent_view:SubmitButton')
    async def green(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with SatanBot.lock:
            SatanBot.victims[self.victim_id]['gift'] = self.puzzle_post
        log(f'Puzzle post submitted for {self.victim_id}: {self.puzzle_post}')
        await interaction.response.send_message('Your puzzle has been saved! If you think of anything that needs changing before Dec 22th, send me another full message with images and files attached and we can replace the existing submission.')

