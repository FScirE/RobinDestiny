"""
This file is used for writing code to test random things in
the Bungie.Net API without starting the discord bot
"""

from dotenv import get_key
import src.destiny as destiny

print("start")
destiny.setup_destiny_data()
#destiny.get_character_data_account_embed("Tom", "2842")
# info = {
#         "displayName": "Tom",
#         "displayNameCode": "3209"
#     }
# account_data = destiny.post_request_response("/Destiny2/SearchDestinyPlayerByBungieName/-1/", info)
# membership_type = account_data[0]["membershipType"]
# membership_id = account_data[0]["membershipId"]
# data = destiny.get_request_response(f"/Destiny2/{membership_type}/Profile/{membership_id}?components={destiny.component_types['Characters']},{destiny.component_types['Profiles']}")
# first_key = next(iter(data["characters"]["data"]))
# emblem_hash = data["characters"]["data"][first_key]["emblemHash"]
# emblem_data = destiny.get_request_response(f"/Destiny2/Manifest/DestinyInventoryItemDefinition/{emblem_hash}/")
info = {
    "displayNamePrefix": "Tom"
}
data = destiny.post_request_response(f"/User/Search/GlobalName/0/", info)
print("end")
