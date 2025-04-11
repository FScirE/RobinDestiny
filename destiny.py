import requests
import json
import os
from datetime import datetime, timezone
from dotenv import get_key

DESTINY_API_KEY = get_key("./.env", "DESTINY_API_KEY")
ROOT = "https://www.bungie.net/Platform"
HEADER = {
    "X-API-KEY": DESTINY_API_KEY,
    "Content-Type": "application/json"
}

hashes = {
    "Nightfall": "2029743966"
}

''''
Get response from GET request to bungie API
'''
def get_request_response(path):
    data = requests.get(ROOT + path, headers=HEADER)
    return data.json()["Response"]

''''
Get response from POST request to bungie API
'''
def post_request_response(path, payload):
    data = requests.post(ROOT + path, json=payload, headers=HEADER)
    return data.json()["Response"]

'''
Write json data to file
'''
def write_data_file(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

'''
Read data from json file
'''
def read_data_file(filepath):
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        print(e)
        return None
    else:
        return data

'''
Reads end date of grandmaster entry (could be any) in milestones to see if data needs updating
'''
def is_next_week():
    data = read_data_file("data/milestones.json")
    if data is None: #no existing data
        print("No existing data")
        return True
    entry = data[hashes["Nightfall"]]
    entry_endtime = datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > entry_endtime:
        print("Data is outdated")
        return True
    return False

'''
Setup destiny json data
'''
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
