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

# token = destiny.get_set_oauth()
# m_type = get_key(".env", "MEMBERSHIP_TYPE")
# m_id = get_key(".env", "MEMBERSHIP_ID")
# ch_id = get_key(".env", "HUNTER_ID")
# data = destiny.get_request_response_oauth(f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/Vendors/{destiny.hashes['Eververse']}/" +
#                             f"?components={destiny.component_types['VendorCategories']}," +
#                             f"{destiny.component_types['VendorSales']}", token)

print("end")
