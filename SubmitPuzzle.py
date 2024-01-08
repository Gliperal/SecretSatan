import discord

from DropOut import DropOutButton
from EmergencyVolunteer import EmergencyVolunteerButton
from logfile import log
from PuzzlePost import PuzzlePost
from SatanBot import SatanBot

class SubmitPuzzleButton(discord.ui.Button):
    def __init__(self, victim):
        name = victim['preferences']['handle']
        label = f'Submit last post as a puzzle for {name}'
        if 'gift' in victim:
            if len(label) > 50:
                label = label[:50]
            label += ' (replacing the existing gift)'
        if len(label) > 80:
            label = label[:80]
        super().__init__(label=label, style=discord.ButtonStyle.green) # custom_id='persistent_view:SubmitButton'
        self.victim_id = victim['user_id']

    async def callback(self, interaction):
        async for message in interaction.channel.history(limit=10):
            if message.author == interaction.user:
                puzzle_post = PuzzlePost.fromMessage(message)
                if len(puzzle_post.content) > 2000:
                    await interaction.response.send_message('Sorry, I can\'t handle messages longer than 2000 characters. Consider attaching a file if you need the extra space.')
                    return
                async with SatanBot.lock:
                    victim = SatanBot.get_user(self.victim_id)
                    victim['gift'] = puzzle_post
                log(f'Puzzle post submitted for {self.victim_id}: {puzzle_post}')
                await puzzle_post.send(interaction.user)
                await interaction.response.send_message('Your puzzle has been saved! See a preview of what it will look like above. If you think of anything that needs changing before Dec 22th, send me another full message with images and files attached and click the button to replace the existing submission.')
                return
        await interaction.response.send_message('Failed to find message.')

class SubmitPuzzleView(discord.ui.View):
    def __init__(self, satan, victims):
        super().__init__(timeout=None)
        for victim in victims:
            self.add_item(SubmitPuzzleButton(victim))
        if 'emergency_satan' not in satan or not satan['emergency_satan']:
            self.add_item(EmergencyVolunteerButton())
        self.add_item(DropOutButton())
