"""
This file is used for writing code to test random things in
the Bungie.Net API without starting the discord bot
"""

from dotenv import get_key
import requests
import src.destiny as destiny
import base64

print("start")
destiny.setup_destiny_data()
# info = {
#     "displayNamePrefix": "Tom"
# }
# data = destiny.post_request_response(f"/User/Search/GlobalName/0/", info)
# data = destiny.get_request_response("/Destiny2/Vendors?components=400")
access = destiny.get_bearer("3d3e5452083fde16b6cf5e27340abe96")
m_type = get_key(".env", "MEMBERSHIP_TYPE")
m_id = get_key(".env", "MEMBERSHIP_ID")
ch_id = get_key(".env", "CHARACTER_ID")
header = {**destiny.HEADER, **{"Authorization": "Bearer " + access}}
data = requests.get(destiny.ROOT + f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/Vendors/{destiny.hashes['Zavala']}/?components={destiny.component_types['VendorCategories']}", headers=header).json()["Response"]
print("end")
