import requests
import json
import os
import base64
import io
import shutil
from PIL import Image
from datetime import datetime, timezone, timedelta
from dotenv import get_key

DESTINY_API_KEY = get_key(".env", "DESTINY_API_KEY")
ROOT = "https://www.bungie.net/Platform"
IMG_ROOT = "https://www.bungie.net"
HEADER = {
    "X-API-KEY": DESTINY_API_KEY,
    "Content-Type": "application/json"
}

DATA_FOLDER = "data"
MILESTONES_FILE = os.path.join(DATA_FOLDER, "milestones.json")
GM_FILE = os.path.join(DATA_FOLDER, "grandmaster.json")
DESTINATION_FILE = os.path.join(DATA_FOLDER, "gmdestination.json")
MODIFIERS_FOLDER = os.path.join(DATA_FOLDER, "gm_modifiers")
GM_WEAPON_FILE = os.path.join(DATA_FOLDER, "gmweapon.json")
OAUTH_FILE = "./oauth.json"
EVERVERSE_FOLDER = os.path.join(DATA_FOLDER, "eververse")
RAID_DUNGEON_FOLDER = os.path.join(DATA_FOLDER, "raid_dungeon")

BRIGHT_DUST_URL = IMG_ROOT + "/common/destiny2_content/icons/555d03d9dde55e4015d76a67f1c763e2.png"
KINETIC_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_3385a924fd3ccb92c343ade19f19a370.png"
ARC_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_092d066688b879c807c3b460afdd61e6.png"
SOLAR_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_2a1773e10968f2d088b97c22b22bba9e.png"
VOID_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_ceb2f6197dccf3958bb31cc783eb97a0.png"
STASIS_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_530c4c3e7981dc2aefd24fd3293482bf.png"
STRAND_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_b2fe51a94f3533f97079dfa0d27a4096.png"

NIGHTFALL_URL = IMG_ROOT + "/common/destiny2_content/icons/3642cf9e2acd174dcab5b5f9e3a3a45d.png"
RAID_URL = IMG_ROOT + "/common/destiny2_content/icons/bd7a1fc995f87be96698263bc16698e7.png"
DUNGEON_URL = IMG_ROOT + "/common/destiny2_content/icons/b5c87175a97d1333da0ff4300fb87f57.png"

elements = {
    1: ("Kinetic", KINETIC_URL),
    2: ("Arc", ARC_URL),
    3: ("Solar", SOLAR_URL),
    4: ("Void", VOID_URL),
    6: ("Stasis", STASIS_URL),
    7: ("Strand", STRAND_URL)
}
platforms = {
    1: "Xbox",
    2: "Playstation",
    3: "Steam",
    4: "Battle.net",
    5: "Stadia",
    6: "Epic Games"
}
component_types = {
    "Profiles": 100,
    "Characters": 200,
    "CharacterActivities": 204,
    "CharacterEquipment": 205,
    "ItemInstances": 300,
    "ItemPerks": 302,
    "ItemStats": 304,
    "Vendors": 400,
    "VendorCategories": 401,
    "VendorSales": 402
}
hashes = {
    #"Nightfall": "2029743966",
    "FocusedDecoding": "2232145065",
    "Eververse": "3361454721",
    "Xur": "2190858386",
    "Dungeon": "608898761",
    "Raid": "2043403989"
}
classes = {
    671679327 : "Hunter",
    2271682572 : "Warlock",
    3655393761 : "Titan"
}

def get_request_response(path):
    """
    Get response from GET request to bungie API
    """
    data = requests.get(ROOT + path, headers=HEADER)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]

def post_request_response(path, payload):
    """
    Get response from POST request to bungie API
    """
    data = requests.post(ROOT + path, json=payload, headers=HEADER)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]

def write_data_file(data, filepath):
    """
    Write json data to file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def read_data_file(filepath):
    """
    Read data from json file
    """
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except FileNotFoundError as e:
        return None
    else:
        return data

def get_manifest_data(entry, hash):
    """
    Gets data from manifest
    """
    data = get_request_response(f"/Destiny2/Manifest/Destiny{entry}Definition/{hash}/")
    return data

def get_request_response_oauth(path, access_token):
    """
    Get response from GET request with OAuth requirement with access key and components
    """
    header = {**HEADER, **{"Authorization": "Bearer " + access_token}}
    data = requests.get(ROOT + path, headers=header)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]


def check_refresh_token():
    """
    Checks if refresh token exists or if outdated
    """
    if not os.path.isfile(OAUTH_FILE):
        return False
    data = read_data_file(OAUTH_FILE)
    expiry_date = datetime.fromisoformat(data["expiryDate"])
    if datetime.now(timezone.utc) > expiry_date:
        return False
    return True

def data_outdated_incomplete(): #check if any folder or file is missing
    """
    Checks if all data exists and reads end date of first
    entry in milestones to see if data needs updating
    """
    if (not os.path.isdir(DATA_FOLDER) or
        not os.path.isdir(MODIFIERS_FOLDER) or
        not os.path.isfile(MILESTONES_FILE) or
        not os.path.isfile(GM_FILE) or
        not os.path.isfile(DESTINATION_FILE) or
        not os.path.isfile(GM_WEAPON_FILE) or
        not os.path.isdir(EVERVERSE_FOLDER) or
        not os.path.isdir(RAID_DUNGEON_FOLDER)):
        print("Data is incomplete")
        return True
    milestone_data = read_data_file(MILESTONES_FILE)
    first = list(milestone_data)[0]
    entry = milestone_data[first]
    entry_endtime = datetime.fromisoformat(entry["endDate"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > entry_endtime:
        print("Data is outdated")
        return True
    return False


def setup_destiny_data():
    """
    Setup weekly Destiny json data
    """
    print("Setting up destiny data...")

    m_type = get_key(".env", "MEMBERSHIP_TYPE")
    m_id = get_key(".env", "MEMBERSHIP_ID")
    ch_ids = {
        "hunter": get_key(".env", "HUNTER_ID"),
        "warlock": get_key(".env", "WARLOCK_ID"),
        "titan": get_key(".env", "TITAN_ID")
    }

    #check if data is up to date and complete
    if not data_outdated_incomplete():
        print("Using existing data!")
        return True

    #check valid refresh key exist else create new one to get access key
    if not check_refresh_token():
        auth_key = input("  Input authorization key: ")
        access_token = get_set_oauth(auth_key)
    else:
        access_token = get_set_oauth()
    if access_token is None:
        print("  Failed getting access token")
        return False
    print("  Access token acquired")

    #clear any incomplete data
    if os.path.isdir(DATA_FOLDER):
        shutil.rmtree(DATA_FOLDER)

    print("Gathering data from Bungie.Net API:")

    #milestones.json, for checking if up to date in the future
    print("  Getting milestones...")
    milestones_data = get_request_response("/Destiny2/Milestones/")
    write_data_file(milestones_data, MILESTONES_FILE)

    #grandmaster.json
    print("  Getting grandmaster...")
    character_data = get_request_response_oauth(f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_ids['titan']}/" + #i dont play titan
                                f"?components={component_types['CharacterActivities']}", access_token)
    activities = character_data["activities"]["data"]["availableActivities"]
    found = False
    for activity in activities:
        if "modifierHashes" not in activity or len(activity["modifierHashes"]) <= 11: #speed up search
            continue
        nightfall_hash = activity["activityHash"]
        nightfall_data = get_manifest_data("Activity", nightfall_hash)
        if nightfall_data["displayProperties"]["name"] == "Nightfall: Grandmaster":
            found = True
            print("    Found!")
            write_data_file(nightfall_data, GM_FILE)
            break
    if not found: #gm not found
        print("    Not found.")
        write_data_file({}, GM_FILE)
        write_data_file({}, MILESTONES_FILE)
        os.mkdir(MODIFIERS_FOLDER)
    else:
        #gmdestination.json
        print("  Getting gm destination...")
        destination_data = get_manifest_data("Destination", nightfall_data["destinationHash"])
        write_data_file(destination_data, DESTINATION_FILE)

        #grandmaster modifiers
        print("  Getting gm modifiers...")
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
                # width = 0
                # for item in modifier_data["displayProperties"]["iconSequences"]:
                #     for url in item["frames"]:
                #         image_data = requests.get(IMG_ROOT + url).content
                #         image = Image.open(io.BytesIO(image_data))
                #         if image.width > width:
                #             width = image.width
                #             modifier_data["displayProperties"]["icon"] = url
                write_data_file(modifier_data, os.path.join(MODIFIERS_FOLDER, str(modifier_hash) + ".json"))

    #raids and dungeons
    print("  Getting raids and dungeons...")
    for activity in activities:
        if "challenges" not in activity: #this fails if you have completed the pinnacle already
            continue
        activity_hash = activity["activityHash"]
        activity_data = get_manifest_data("Activity", activity_hash)
        activity_type_hash = activity_data["activityTypeHash"]
        if str(activity_type_hash) in [hashes["Raid"], hashes["Dungeon"]]:
            if (("selectionScreenDisplayProperties" in activity_data and activity_data["selectionScreenDisplayProperties"]["name"] != "Master") or
                "selectionScreenDisplayProperties" not in activity_data):
                #get destination info and add into activity data
                destination_data = get_manifest_data("Destination", activity_data["destinationHash"])
                destination_name = destination_data["displayProperties"]["name"]
                activity_data["destinationName"] = destination_name
                write_data_file(activity_data, os.path.join(RAID_DUNGEON_FOLDER, f"{activity_hash}.json"))

    #nightfall weapon
    print("  Getting gm weapon...")
    focusing_data = get_request_response_oauth(f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_ids['hunter']}/Vendors/{hashes['FocusedDecoding']}/" +
                                f"?components={component_types['VendorCategories']}," +
                                f"{component_types['VendorSales']}", access_token)
    categories = focusing_data["categories"]["data"]["categories"]
    for category in categories:
        #category id 2 = featured nf weapon shop
        if category["displayCategoryIndex"] == 2:
            item_idx = category["itemIndexes"][1] #second item is adept
            item = focusing_data["sales"]["data"][str(item_idx)]
            item_data = get_manifest_data("InventoryItem", item["itemHash"])
            write_data_file(item_data, GM_WEAPON_FILE)
            break

    #eververse weeklies
    print("  Getting eververse:")
    gathered = [] #keep track of item hashes to ignore shared items
    for key, ch_id in ch_ids.items():
        print(f"    {key.title()}...")
        eververse_data = get_request_response_oauth(f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/Vendors/{hashes['Eververse']}/" +
                            f"?components={component_types['VendorCategories']}," +
                            f"{component_types['VendorSales']}", access_token)
        #category id 2 = featured bright dust
        #category id 9 = bright dust items
        #category id 10 = bright dust flair
        categories = eververse_data["categories"]["data"]["categories"]
        for category in categories:
            if category["displayCategoryIndex"] in [2, 9, 10]: #add items from the 3 eververse bright dust weekly shops
                for item_idx in category["itemIndexes"]:
                    item = eververse_data["sales"]["data"][str(item_idx)]
                    item_hash = item["itemHash"]
                    price = item["costs"][0]["quantity"]
                    if item_hash in gathered: #ignore shared items
                        continue
                    item_data = get_manifest_data("InventoryItem", item_hash)
                    item_data["price"] = price #add bright dust price
                    item_data
                    if item_data["itemTypeDisplayName"] == "Consumable":
                        continue
                    gathered.append(item_hash)
                    write_data_file(item_data, os.path.join(EVERVERSE_FOLDER, str(item_hash) + ".json"))
    print("Done!")
    return True

def get_account_data(name, tag):
    """
    Gets account data from name and tag
    """
    info = {
        "displayName": name,
        "displayNameCode": tag
    }
    account_data = post_request_response("/Destiny2/SearchDestinyPlayerByBungieName/-1/", info)
    return account_data

def get_characters_data(type, id):
    """
    Gets the characters for a given account
    """
    response = get_request_response(f"/Destiny2/{type}/" +
                                    f"Profile/{id}/" +
                                    f"?components={component_types['Characters']}")
    if not response:
        return None
    return response["characters"]["data"]

def get_rarity_color(item):
    """
    Get the rarity color of a given InventoryItem as r,g,b
    """
    rarity = item["inventory"]["tierTypeName"]
    if rarity == "Exotic":
        return 205, 173, 54
    elif rarity == "Legendary":
        return 79, 54, 99
    else: #Rare
        return 86, 126, 157

def get_set_oauth(code = None):
    """
    Gets OAuth access token given an authentication code, or using refresh token,
    and saves refresh token to file
    (psa: authentication code is one time use)
    """
    url = "https://www.bungie.net/platform/app/oauth/token/"
    id = get_key(".env", "CLIENT_ID")
    secret = get_key(".env", "CLIENT_SECRET")

    get = code is None

    coded = base64.b64encode(f"{id}:{secret}".encode()).decode("ascii")
    header = {
        "Authorization": "Basic " + coded,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    if get: #if no auth code provided use refresh token
        info = {
            "grant_type": "refresh_token",
            "refresh_token": read_data_file(OAUTH_FILE)["token"]
        }
    else:
        info = {
            "grant_type": "authorization_code",
            "code": code
        }
    data = requests.post(url, data=info, headers=header).json()
    if "error" in data:
        return None

    refresh_data = {
        "token": data["refresh_token"],
        "expiryDate": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
    }
    write_data_file(refresh_data, OAUTH_FILE)
    return data["access_token"]
