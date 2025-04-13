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
destiny.setup_destiny_data()

# access = destiny.get_bearer("aed514ebdec439875d60ac937e0906a8")
# m_type = get_key(".env", "MEMBERSHIP_TYPE")
# m_id = get_key(".env", "MEMBERSHIP_ID")
# ch_id = get_key(".env", "CHARACTER_ID")
# header = {**destiny.HEADER, **{"Authorization": "Bearer " + access}}
# data = requests.get(destiny.ROOT + f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/Vendors/?components={destiny.component_types['VendorSales']}", headers=header).json()["Response"]
# for key, item in data["sales"]["data"].items():
#     item_hash = item["itemHash"]
#     item_data = destiny.get_request_response(f"/Destiny2/Manifest/DestinyInventoryItemDefinition/{item_hash}")
#     destiny.write_data_file(item_data, f"data/items/{key}-{item_hash}.json")

# data = destiny.read_data_file("data/gm_modifiers/1806568190.json")
# desc = data["displayProperties"]["description"]
# formatted = re.sub(r"\{[^\{\}]*\}", "25", desc)
# formatted = re.sub(r"\[[^\[\]]*\] ", "", formatted)
# print(formatted)

# embeds.get_gm_data_embeds()

print("end")
