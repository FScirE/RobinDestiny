"""
This file is used for writing code to test random things in
the Bungie.Net API without starting the discord bot
"""

from dotenv import get_key
import destiny

print("start")
destiny.setup_destiny_data()
#destiny.get_character_data_account_embed("Tom", "2842")
info = {
        "displayName": "Tom",
        "displayNameCode": "2842"
    }
account_data = destiny.post_request_response("/Destiny2/SearchDestinyPlayerByBungieName/-1/", info)
membership_type = account_data[0]["membershipType"]
membership_id = account_data[0]["membershipId"]
data = destiny.get_request_response(f"/Destiny2/{membership_type}/Profile/{membership_id}?components=200")
print("end")
