import discord

from logfile import log
from SatanBot import SatanBot

class SubmitPuzzleButton(discord.ui.Button):
    def __init__(self, victim):
        super().__init__(label=label, style=discord.ButtonStyle.green) # custom_id='persistent_view:SubmitButton'
        self.victim_id = victim['user_id']
        name = victim['preferences']['name']
        label = f'Submit your most recent post as a puzzle for {name}'
        if 'gift' in victim:
            label += ' (replacing the existing gift)'

    async def callback(interaction):
        puzzle_post = PuzzlePost(most_recent_post_from_user)
        async with SatanBot.lock:
            SatanBot.victims[self.victim_id]['gift'] = puzzle_post
        log(f'Puzzle post submitted for {self.victim_id}: {puzzle_post}')
        await interaction.response.send_message('Your puzzle has been saved! See a preview of what it will look like above. If you think of anything that needs changing before Dec 22th, send me another full message with images and files attached and click the button to replace the existing submission.')

class SubmitPuzzleView(discord.ui.View):
    def __init__(self, satan, victims):
        super().__init__(timeout=None)
        for victim in victims:
            self.add_item(SubmitPuzzleButton(victim))
        if 'emergency_satan' not in satan or not satan['emergency_satan']:
            self.add_item('Volunteer as emergency satan')
        self.add_item('Drop out')
