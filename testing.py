"""
This file is used for writing code to test random things in
the Bungie.Net API without starting the discord bot
"""

from dotenv import get_key
import destiny

destiny.setup_destiny_data()
destiny.get_character_data_account_embed("FScirE", "0322")
