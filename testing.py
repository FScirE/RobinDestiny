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

# for activity in data["activities"]["data"]["availableActivities"]:
#     if "challenges" not in activity:
#         continue
#     manifest_data = destiny.get_manifest_data("Activity", activity["activityHash"])
#     if (
#         str(manifest_data["activityTypeHash"]) in [destiny.hashes["Raid"], destiny.hashes["Dungeon"]] and
#         "selectionScreenDisplayProperties" in manifest_data and
#         manifest_data["selectionScreenDisplayProperties"]["name"] != "Master"
#         ):
#         destiny.write_data_file(manifest_data, f"data/test/{activity['activityHash']}.json")

# data = destiny.get_request_response("/Content/Rss/NewsArticles/0/?categoryfilter=updates")

# for article in data["NewsArticles"]:
#     title = article["Title"]
#     link = article["Link"]
#     description = article["Description"]
#     date = datetime.fromisoformat(article["PubDate"].replace("Z", "+00:00")).date()
#     print(f"{date}")

print("end")
