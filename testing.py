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

access = destiny.get_bearer("812b1fa33d3f66446935bdf85e2bb13c")
m_type = get_key(".env", "MEMBERSHIP_TYPE")
m_id = get_key(".env", "MEMBERSHIP_ID")
ch_id = get_key(".env", "CHARACTER_ID")
header = {**destiny.HEADER, **{"Authorization": "Bearer " + access}}
data = requests.get(destiny.ROOT + f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/Vendors/{destiny.hashes['Eververse']}/" +
                    f"?components={destiny.component_types['Vendors']}" +
                    f",{destiny.component_types['VendorCategories']}," +
                    f"{destiny.component_types['VendorSales']}", headers=header).json()["Response"]
destiny.write_data_file(data, destiny.DATA_FOLDER + "/eververse.json")

# data = destiny.read_data_file("data/gm_modifiers/1806568190.json")
# desc = data["displayProperties"]["description"]
# formatted = re.sub(r"\{[^\{\}]*\}", "25", desc)
# formatted = re.sub(r"\[[^\[\]]*\] ", "", formatted)
# print(formatted)

data = destiny.read_data_file("data/eververse.json")
categories = data["categories"]["data"]["categories"]
categories = sorted(categories, key = lambda k : k["displayCategoryIndex"])
for category in categories:
    if category["displayCategoryIndex"] in [2, 9, 10]:
        i = 0
        for item_idx in category["itemIndexes"]:
            item_hash = data["sales"]["data"][str(item_idx)]["itemHash"]
            item_data = destiny.get_manifest_data("InventoryItem", item_hash)
            destiny.write_data_file(item_data, f"data/category{category['displayCategoryIndex']}/item{i}.json")
            i += 1

# embeds.get_gm_data_embeds()

vendor_data = destiny.get_manifest_data("Vendor", destiny.hashes["Eververse"])

print("end")
