import requests
import json
import os
import base64
from datetime import datetime, timezone
from dotenv import get_key

DESTINY_API_KEY = get_key(".env", "DESTINY_API_KEY")
AUTH_CODE = get_key(".env", "OAUTH_CODE")
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
    nightfall_hash = milestones_data[hashes["Nightfall"]]["activities"][-1]["activityHash"] #last activity listed in nightfalls is grandmaster
    nightfall_data = get_request_response(f"/Destiny2/Manifest/DestinyActivityDefinition/{nightfall_hash}/")
    write_data_file(nightfall_data, "data/grandmaster.json")

    #grandmaster modifiers
    for modifier in nightfall_data["modifiers"]:
        modifier_hash = modifier["activityModifierHash"]
        modifier_data = get_request_response(f"/Destiny2/Manifest/DestinyActivityModifierDefinition/{modifier_hash}")
        ignored_modifiers = [ #irrelevant or incorrect modifiers
            "Double Nightfall Drops",
            "Increased Vanguard Rank",
            "Shielded Foes",
            "Chaff",
            "Randomized Banes"
        ]
        if modifier_data["displayInNavMode"] and modifier_data["displayProperties"]["name"] not in ignored_modifiers:
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
