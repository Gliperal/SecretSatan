# Stolen from https://github.com/BenceJoful/find-lonely-puzzles/blob/main/SearchReactions.py

import discord
from dotenv import load_dotenv
import os
import traceback

from util import message_Admin
from logfile import log
from SatanBot import SatanBot, State

load_dotenv()
ADMIN = os.getenv('ADMIN')

class DropOutButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Drop Out', style=discord.ButtonStyle.green, custom_id='persistent_view:DropOutButton')
    async def orange(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DropOutFormModal())

class DropOutFormModal(discord.ui.Modal, title='Drop Out'):
    form_confirm = discord.ui.TextInput(
        label='By dropping out of Secret Satan, any victim(s) that have already been assigned to you will be given to one of our emergency setters instead... Are you sure you want to do this? Type "confirm" in the box to confirm your intention to leave.',
        required=True,
        style=discord.TextStyle.short,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if self.form_confirm.value != 'confirm':
                return
            if SatanBot.state == State.RANDOMIZING:
                await interaction.response.send_message('Sorry, victims are already being assigned! Try again in a few minutes.')
                return
            if SatanBot.state == State.DELIVERING:
                await interaction.response.send_message('Can\'t do that right now!')
                return
            user_id = str(interaction.user.id)

            #save in database
            async with SatanBot.lock:
                if SatanBot.state != State.RECRUITING and SatanBot.state != State.SETTING:
                    raise Exception('Unknown state ' + SatanBot.state)
                satan = SatanBot.get_satan(user_id)
                satan['satan'] = False
                satan['emergency_satan'] = False
                if SatanBot.state == State.SETTING:
                    # reassign victims to emergency satans
                    victims = SatanBot.get_victims_of(user_id) but only the ones without puzzles
                    while len(victims) > 0:
                        victim = victims.pop()
                        victim['satan'] = SatanBot.get_underworked_emergency_satans()[0]

            #log and inform user
            log(f'{user_id} dropped out.')
            await interaction.response.send_message('Successfully dropped out. Sorry to see you go!')
        except:
            await message_Admin('Error in processing drop out form submission', embed=discord.Embed(description=traceback.format_exc()))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        await message_Admin('Error in drop out form', embed=discord.Embed(description=traceback.format_exc(error)))

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)
