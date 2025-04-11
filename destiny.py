import requests
import json
import os
from datetime import datetime, timezone, timedelta
from dotenv import get_key
from discord import Embed, Colour

DESTINY_API_KEY = get_key("./.env", "DESTINY_API_KEY")
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
}
hashes = {
    "Nightfall": "2029743966",
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
Gets account and character information and builds discord embed elements
"""
def get_account_data(name, tag):
    info = {
        "displayName": name,
        "displayNameCode": tag
    }
    account_data = post_request_response("/Destiny2/SearchDestinyPlayerByBungieName/-1/", info)
    return account_data
def get_character_data_account_embed(name, tag):
    #get account data
    account_data = get_account_data(name, tag)
    if not account_data:
        return None

    #select primary profile (either cross saved primary or first in list)
    if "crossSaveOverride" in account_data[0]:
        membership_type = account_data[0]["crossSaveOverride"]
        for data in account_data:
            if data["membershipType"] == membership_type:
                membership_id = data["membershipId"]
                membership_url = IMG_ROOT + data["iconPath"]
    else:
        membership_type = account_data[0]["membershipType"]
        membership_id = account_data[0]["membershipId"]
        membership_url = IMG_ROOT + account_data[0]["iconPath"]

    #get characters data
    character_data = get_request_response(f"/Destiny2/{membership_type}/" +
                                          f"Profile/{membership_id}" +
                                          f"?components={component_types['Characters']}")

    #start building embeds
    embeds = []
    embeds.append(
        Embed(
            title=f"{name}#{str(tag).zfill(4)}"
        )
        .set_author(name=f"Platform: {platforms[membership_type]}", icon_url=membership_url)
    )
    for _, character in character_data["characters"]["data"].items():
        minutes = int(character["minutesPlayedTotal"])
        guardian_class = classes[character["classHash"]]
        power = character["light"]
        emblem_url = IMG_ROOT + character["emblemPath"]

        #copy emblem color
        r = character["emblemColor"]["red"]
        g = character["emblemColor"]["green"]
        b = character["emblemColor"]["blue"]

        #time since last played
        last = datetime.fromisoformat(character["dateLastPlayed"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - last

        embeds.append(
            Embed(
                title=f"{power} | {guardian_class}",
                #⣠⡾⠋⠙⢷⣄⣠⡾⠋⠙⢷⣄⣠⡾⠋⠙⢷⣄⣠⡾⠋⠙⢷⣄
                #description="\u28e0\u287e\u280b\u2819\u28B7\u28C4\u28e0\u287e\u280b\u2819\u28B7\u28C4\u28e0\u287e\u280b\u2819\u28B7\u28C4\u28e0\u287e\u280b\u2819\u28B7\u28C4",
                description="\u2802"*24,
                color=Colour.from_rgb(r, g, b)
            )
            .add_field(name="Total time played", value=f"{minutes//60}h {minutes%60}m", inline=False)
            .add_field(name="Time since last played", value=format_timedelta(diff), inline=False)
            .set_thumbnail(url=emblem_url)
        )
    return embeds

"""
Formats a datetime object for pretty printing
"""
def format_timedelta(time: timedelta):
    days = time.days
    hours = time.seconds // 3600
    minutes = (time.seconds % 3600) // 60

    return_str = ""
    if days > 0:
        return_str += f"{days}d"
        return_str += f" {hours}h"
        return_str += f" {minutes}m"
    elif hours > 0:
        return_str += f"{hours}h"
        return_str += f" {minutes}m"
    elif minutes > 7:
        return_str += f"{minutes}m"
    else:
        return_str += "Now"

    return return_str

