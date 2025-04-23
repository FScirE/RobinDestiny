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

print("start")
# destiny.setup_destiny_data()

# data = destiny.get_manifest_data("Stat", "3897883278")
# print(data)

# data = destiny.get_account_data("FScirE", "0322")

# data = destiny.get_manifest_data("DamageType", "3949783978")

# payload = {
#     "displayNamePrefix": "Tom"
# }
# data = destiny.post_request_response("/User/Search/GlobalName/0/", payload)

# token = destiny.get_set_oauth()
# m_type = get_key(".env", "MEMBERSHIP_TYPE")
# m_id = get_key(".env", "MEMBERSHIP_ID")
# ch_id = get_key(".env", "HUNTER_ID")
# data = destiny.get_request_response_oauth(f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/" +
#                                 f"?components={destiny.component_types['CharacterActivities']}", token)

print("end")
