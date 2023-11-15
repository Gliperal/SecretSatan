import discord
import traceback

from util import message_Admin
from logfile import log
from SatanBot import SatanBot, State

from send_setter_message import send_setter_message

class EmergencyVolunteerButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='Volunteer as an emergency satan', style=discord.ButtonStyle.blurple) # custom_id='persistent_view:SubmitButton'

    async def callback(self, interaction):
        await interaction.response.send_modal(EmergencyVolunteerFormModal())

class EmergencyVolunteerFormModal(discord.ui.Modal, title='Drop Out'):
    form_confirm = discord.ui.TextInput(
        label='Commit to making emergency puzzles as needed?',
        required=True,
        placeholder='yes',
        style=discord.TextStyle.short,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if self.form_confirm.value.lower() not in ['confirm', 'yes', 'y']:
                await interaction.response.send_message('Please type \"yes\" into the box if you intend on volunteering. Emergency setter addition cancelled.')
                return

            #save in database
            user_id = str(interaction.user.id)
            async with SatanBot.lock:
                satan = SatanBot.get_user(user_id)
                satan['emergency_satan'] = True

            #log and inform user
            log(f'{user_id} registered as emergency satan.')
            async with SatanBot.lock:
                victims = SatanBot.get_victims()
                abandoned = [v for v in victims if v['satan'] is None]
                if (len(abandoned) == 0):
                    await interaction.response.send_message('Thank you for volunteering! You will be contacted if any additional victims are assigned to you.')
                else:
                    for victim in abandoned:
                        victim['satan'] = user_id
                    await interaction.response.send_message('Thank you for volunteering! You have had some additional victims are assigned to you:')
                    await send_setter_message(user_id)
        except:
            await message_Admin('Error in processing drop out form submission', embed=discord.Embed(description=traceback.format_exc()))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        await message_Admin('Error in emergency volunteer form', embed=discord.Embed(description=traceback.format_exc(error)))

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)
