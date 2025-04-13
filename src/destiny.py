import requests
import json
import os
import base64
import io
from PIL import Image
from datetime import datetime, timezone
from dotenv import get_key

DESTINY_API_KEY = get_key(".env", "DESTINY_API_KEY")
ROOT = "https://www.bungie.net/Platform"
IMG_ROOT = "https://www.bungie.net"
HEADER = {
    "X-API-KEY": DESTINY_API_KEY,
    "Content-Type": "application/json"
}

platforms = {
    1: "Xbox",
    2: "Playstation",
    3: "Steam",
    6: "Epic Games"
}
component_types = {
    #for profile and character
    "Profiles": 100,
    "Characters": 200,
    #for equippead weapon (future effective mag)
    "CharacterEquipment": 205,
    "ItemPerks": 302,
    "itemStats": 304,
    #for vendors
    "Vendors": 400,
    "VendorCategories": 401,
    "VendorSales": 402
}
hashes = {
    "Nightfall": "2029743966",
    "Zavala": "69482069"
}
classes = {
    671679327 : "Hunter",
    2271682572 : "Warlock",
    3655393761 : "Titan"
}

"""
Get response from GET request to bungie API
"""
def get_request_response(path):
    data = requests.get(ROOT + path, headers=HEADER)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]

"""
Get response from POST request to bungie API
"""
def post_request_response(path, payload):
    data = requests.post(ROOT + path, json=payload, headers=HEADER)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]

"""
Write json data to file
"""
def write_data_file(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

"""
Read data from json file
"""
def read_data_file(filepath):
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        return None
    else:
        return data

"""
Reads end date of grandmaster entry (could be any) in milestones to see if data needs updating
"""
def is_next_week():
    data = read_data_file("data/milestones.json")
    if not data: #no existing data
        print("No existing data")
        return True
    entry = data[hashes["Nightfall"]]
    entry_endtime = datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > entry_endtime:
        print("Data is outdated")
        return True
    return False

"""
Setup destiny json data
"""
def setup_destiny_data():
    print("Setting up destiny data...")

    #check dates (also if no data exists)
    if not is_next_week():
        print("Using existing data!")
        return

    print("Gathering data from Bungie.Net API...")

    #milestones.json, for checking if up to date in the future
    milestones_data = get_request_response("/Destiny2/Milestones/")
    write_data_file(milestones_data, "data/milestones.json")

    #grandmaster.json
    activities = milestones_data[hashes["Nightfall"]]["activities"]
    for activity in activities:
        nightfall_hash = activity["activityHash"]
        nightfall_data = get_manifest_data("Activity", nightfall_hash)
        if nightfall_data["displayProperties"]["name"] == "Nightfall: Grandmaster":
            break
    write_data_file(nightfall_data, "data/grandmaster.json")

    #gmdestination.json
    destination_data = get_manifest_data("Destination", nightfall_data["destinationHash"])
    write_data_file(destination_data, "data/gmdestination.json")

    #grandmaster modifiers
    for modifier_hash in activity["modifierHashes"]: #grandmaster.json has additional modifiers that arent active
        modifier_data = get_manifest_data("ActivityModifier", modifier_hash)
        ignored_modifiers = [ #irrelevant and/or incorrect modifiers
            "Double Nightfall Drops",
            "Increased Vanguard Rank",
            "Shielded Foes",
            "Chaff",
            "Randomized Banes"
        ]

        if modifier_data["displayInNavMode"] and modifier_data["displayProperties"]["name"] not in ignored_modifiers:
            #make sure icon url is the larger icon
            width = 0
            for item in modifier_data["displayProperties"]["iconSequences"]:
                for url in item["frames"]:
                    image_data = requests.get(IMG_ROOT + url).content
                    image = Image.open(io.BytesIO(image_data))
                    if image.width > width:
                        width = image.width
                        modifier_data["displayProperties"]["icon"] = url

            write_data_file(modifier_data, f"data/gm_modifiers/{modifier_hash}.json")
    print("Done!")

"""
Gets account data from name and tag
"""
def get_account_data(name, tag):
    info = {
        "displayName": name,
        "displayNameCode": tag
    }
    account_data = post_request_response("/Destiny2/SearchDestinyPlayerByBungieName/-1/", info)
    return account_data

"""
Gets data from manifest
"""
def get_manifest_data(entry, hash):
    data = get_request_response(f"/Destiny2/Manifest/Destiny{entry}Definition/{hash}/")
    return data

"""
Gets OAuth access token given an authentication code
(psa: authentication code is one time use)
"""
def get_bearer(code):
    url = "https://www.bungie.net/platform/app/oauth/token/"
    id = get_key("./.env", "CLIENT_ID")
    secret = get_key("./.env", "CLIENT_SECRET")

    coded = base64.b64encode(f"{id}:{secret}".encode()).decode("ascii")
    header = {
        "Authorization": "Basic " + coded,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    info = {
        "grant_type": "authorization_code",
        "code": code
    }
    data = requests.post(url, data=info, headers=header).json()
    if "error" in data:
        return None
    return data["access_token"]
