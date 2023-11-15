async def send_setter_message(satan_id, message=None, use_embed=True):
    import discord
    from util import get_user_by_id
    from SatanBot import SatanBot

    victims = SatanBot.get_victims_of(satan_id)
    if message is None:
        message = 'Your victim this season:' if len(victims) == 1 else 'Your victims this season:'
    for victim in victims:
        satan_user = await get_user_by_id(satan_id)
        victim_user = await get_user_by_id(victim['user_id'])
        preferences = victim['preferences']
        embed_content = f"Name: {preferences['name']}"+ \
            f"\n\nAbout Them: {preferences['about_you']}"+ \
            f"\n\nPuzzles They Enjoy: {preferences['puzzles_enjoyed']}"+ \
            f"\n\nFavorite Puzzle Types: {preferences['favorite_puzzle_types']}"+ \
            f"\n\nAnything Else: {preferences['anything_else']}"
        if use_embed:
            embed = discord.Embed(description=embed_content)
            await satan_user.send(message, embed=embed)
        else:
            await satan_user.send(message + '\n\n' + embed_content)
        message = ''
