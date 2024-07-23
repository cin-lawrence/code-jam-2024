from discord import Embed, SelectMenu
from discord import User, Member

EMOJI: list[str]= [":green_heart:", ":yellow_heart:", ":blue_heart:", ":purple_heart:", ":heart:"]

def form_embed(user: User | Member) -> Embed:
    """Form the embed to show the user their guess' details."""
    embed = Embed(title= f"{user.name}'s Wordle Guess")

    guesses = ... #list of guesses
    for idx, guess in enumerate(guesses):
        embed.add_field(
            name= f"Guess #{idx + 1}",
            value= (f"")
            )

    return embed

def form_select_menu() -> SelectMenu:
    """Form the SelectMenu for the user to choose length of word."""