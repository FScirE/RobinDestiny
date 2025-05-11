"""
This file is used for writing code to test random things in
the Bungie.Net API without starting the discord bot
"""

from dotenv import get_key
import requests
import src.destiny as destiny
import src.embeds as embeds
import base64
import re
from datetime import datetime

print("start")
# destiny.setup_destiny_data()

# accounts_data = destiny.get_account_data("BReezy", 725)

# _1, _2 = embeds.get_account_data_embeds_weapons("FScirE", 322)
# _3 = embeds.get_top_weapons_embeds(_1, _2)

# m_type = get_key(".env", "MEMBERSHIP_TYPE")
# m_id = get_key(".env", "MEMBERSHIP_ID")
# ch_id = get_key(".env", "HUNTER_ID")

# data = destiny.get_request_response(f"/Destiny2/{m_type}/Account/{m_id}/Character/{ch_id}/Stats/Activities/" +
#                                     f"?count=5&page=0")

print("end")
