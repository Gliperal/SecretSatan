# Stolen from https://github.com/BenceJoful/find-lonely-puzzles/blob/main/SearchReactions.py

import discord
from dotenv import load_dotenv
from util import message_Admin

load_dotenv()
ADMIN = os.getenv('ADMIN')

class SignUpFormModal(discord.ui.Modal, title='Sign Up for Secret Puzzle Satan 2022'):
    form_realName = discord.ui.TextInput(
        label='Real Name (Optional)',
        required=False,
        style=discord.TextStyle.short,
        max_length=100
    )

    form_aboutYou = discord.ui.TextInput(
        label='Please tell Satan a little about yourself!',
        style=discord.TextStyle.long,
        required=True,
        max_length=800
    )

    form_puzzlesEnjoyed = discord.ui.TextInput(
        label='Tell us about what kind of puzzles you enjoy',
        style=discord.TextStyle.long,
        required=True,
        max_length=800
    )

    form_favoritePuzzleTypes = discord.ui.TextInput(
        label='Name some of your favourite puzzle types',
        style=discord.TextStyle.long,
        required=True,
        max_length=800
    )

    form_anythingElse = discord.ui.TextInput(
        label='Anything else you would like to tell Satan!',
        style=discord.TextStyle.long,
        required=False,
        max_length=800
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            name = interaction.user.name
            if self.form_realName.value != "":
                name += f" (real name {self.form_realName.value})"

            embed = discord.Embed(description=f"Name: {name}"+ \
                f"\n\nAbout You: {self.form_aboutYou.value}"+ \
                f"\n\nPuzzles You Enjoy: {self.form_puzzlesEnjoyed.value}"+ \
                f"\n\nFavorite Puzzle Types: {self.form_favoritePuzzleTypes.value}"+ \
                f"\n\nAnything Else: {self.form_anythingElse.value}")

            #send back to user for verification
            await interaction.response.send_message(f"OK, you are all signed up!  \nHere's the information I received. If you need to change any of it, feel free to hit the Sign Up button and fill in the whole form again - we'll only use the newest entry.  \n\nIf you need to cancel for any reason, please contact {ADMIN} as soon as possible. \n\nLooking forward to it!", embed=embed)

            #save in database
            puzzlemessage = {
                    "id" : str(interaction.user.id),
                    "username": interaction.user.name,
                    "signup_realname": self.form_realName.value,
                    "signup_about_you": self.form_aboutYou.value,
                    "signup_puzzles_enjoyed": self.form_puzzlesEnjoyed.value,
                    "signup_favorite_puzzle_types": self.form_favoritePuzzleTypes.value,
                    "signup_anything_else": self.form_anythingElse.value,
                }
            db_items("Santas2022").upsert_item(body=puzzlemessage)

            #send to BenceJoful as backup
            await message_Admin('Sign up by '+str(interaction.user.id), embed=discord.Embed(description=str(puzzlemessage)))
        except:
            await message_Admin('Error in processing sign up form submission', embed=discord.Embed(description=traceback.format_exc()))

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        await message_Admin('Error in sign up form', embed=discord.Embed(description=traceback.format_exc(error)))

        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)

