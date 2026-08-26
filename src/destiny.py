import os
import shutil
from datetime import datetime, timezone, timedelta
from dotenv import get_key
from src.netreq import do_retry_request
from src.oauth import get_oauth_code, get_set_oauth, check_refresh_token
from src.io import write_data_file, read_data_file, timestamp_print

DESTINY_API_KEY = get_key(".env", "DESTINY_API_KEY")
ROOT = "https://www.bungie.net/Platform"
IMG_ROOT = "https://www.bungie.net"
HEADER = {
    "X-API-KEY": DESTINY_API_KEY,
    "Content-Type": "application/json"
}

DATA_FOLDER = "data"
RESETS_FILE = os.path.join(DATA_FOLDER, "resets.json")
GM_FILE = os.path.join(DATA_FOLDER, "grandmaster.json")
GM_DESTINATION_FILE = os.path.join(DATA_FOLDER, "gm_destination.json")
GM_WEAPON_FILE = os.path.join(DATA_FOLDER, "gm_weapon.json")
EVERVERSE_FOLDER = os.path.join(DATA_FOLDER, "eververse")
RAID_DUNGEON_FOLDER = os.path.join(DATA_FOLDER, "raid_dungeon")
DAILY_REWARDS_FOLDER = os.path.join(DATA_FOLDER, "daily_rewards")

BRIGHT_DUST_URL = IMG_ROOT + "/common/destiny2_content/icons/555d03d9dde55e4015d76a67f1c763e2.png"
KINETIC_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_3385a924fd3ccb92c343ade19f19a370.png"
ARC_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_092d066688b879c807c3b460afdd61e6.png"
SOLAR_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_2a1773e10968f2d088b97c22b22bba9e.png"
VOID_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_ceb2f6197dccf3958bb31cc783eb97a0.png"
STASIS_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_530c4c3e7981dc2aefd24fd3293482bf.png"
STRAND_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyDamageTypeDefinition_b2fe51a94f3533f97079dfa0d27a4096.png"

XBOX_URL = IMG_ROOT + "/img/theme/bungienet/icons/xboxLiveLogo.png"
PLAYSTATION_URL = IMG_ROOT + "/img/theme/bungienet/icons/psnLogo.png"
STEAM_URL = IMG_ROOT + "/img/theme/bungienet/icons/steamLogo.png"
BATTLENET_URL = IMG_ROOT + "/img/theme/bungienet/icons/battlenetLogo.png"
STADIA_URL = IMG_ROOT + "/img/theme/destiny/icons/icon_stadia.png"
EPIC_GAMES_URL = IMG_ROOT + "/img/theme/destiny/icons/icon_egs.png"

NIGHTFALL_URL = IMG_ROOT + "/common/destiny2_content/icons/3642cf9e2acd174dcab5b5f9e3a3a45d.png"
VANGUARD_ALERT_URL = IMG_ROOT + "/common/destiny2_content/icons/ba5400e0bef9781f2b2c0fd805345e15.png"
RAID_URL = IMG_ROOT + "/common/destiny2_content/icons/bd7a1fc995f87be96698263bc16698e7.png"
DUNGEON_URL = IMG_ROOT + "/common/destiny2_content/icons/b5c87175a97d1333da0ff4300fb87f57.png"
EVERVERSE_URL = IMG_ROOT + "/common/destiny2_content/icons/23163a74361c916f4446518aa53fd014.png"
LZ_URL = IMG_ROOT + "/common/destiny2_content/icons/DestinyActivityModeDefinition_0aa1d7b0e0ac2c6820036b6b3dde3e5b.png"
ACTIVITY_URL = IMG_ROOT + "/common/destiny2_content/icons/0f123e05bb76068db9ee225b63f698cf.png"
ARMOR_URL = IMG_ROOT + "/common/destiny2_content/icons/b13b34ec9946d36c1d108183e2a0b85a.png"

elements = {
    1: ("Kinetic", KINETIC_URL),
    2: ("Arc", ARC_URL),
    3: ("Solar", SOLAR_URL),
    4: ("Void", VOID_URL),
    6: ("Stasis", STASIS_URL),
    7: ("Strand", STRAND_URL)
}
platforms = {
    1: ("Xbox", XBOX_URL),
    2: ("Playstation", PLAYSTATION_URL),
    3: ("Steam", STEAM_URL),
    4: ("Battle.net", BATTLENET_URL),
    5: ("Stadia", STADIA_URL),
    6: ("Epic Games", EPIC_GAMES_URL)
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
    "GMAlert": "3511848321",
    "GMAlertDifficulty": "1983475410", #difficultyTierCollectionHash
    "VanguardArms": "153857624",
    "Xur": "2190858386",
    "Dungeon": "608898761",
    "Raid": "2043403989"
}
#activity types for daily farmable weapons/armor
activity_types = {
    "Fireteam Ops": [
        1996806804, #quickplay
        556925641 #mission
    ],
    "Pinnacle Ops": [
        1227821118, #exotic mission
        2442898492, #crawl
        2897687202 #onslaught
    ],
    "Arena Ops": [
        2009300208, #quickplay
        904017341 #seasonal arena
    ],
    "Solo Ops": [
        3851289711 #solo ops (+quickplay)
    ],
    "Crucible": [
        728792238, #sparrow racing league
        4088006058 #crucible
    ],
    "Gambit": [
        248695599 #gambit
    ]
}
#eververse bright dust rotators
eververse_vendors = [
    "2168194999", #exotic weapon ornaments
    "2031393824", #exotic and legendary armor ornaments
    "3118972542", #exotic emotes
    "3702989297", #exotic ghost shells
    "4020265966", #exotic ships
    "1105106638", #exotic sparrows/skimmers
    "2184482416", #legendary and rare emotes
    "1446296883", #ghost projections
    "2041776156", #shaders
    "213864513", #transmat effects
]
classes = {
    671679327 : "Hunter",
    2271682572 : "Warlock",
    3655393761 : "Titan"
}

def get_request_response(path: str, cache: bool = True, manifest: bool = False) -> object:
    """
    Get response from GET request to bungie API
    """
    data = do_retry_request(cache, True, ROOT + path, HEADER, manifest=manifest)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]

def post_request_response(path: str, payload: object, cache: bool = True) -> object:
    """
    Get response from POST request to bungie API
    """
    data = do_retry_request(cache, False, ROOT + path, HEADER, payload)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]

def get_manifest_data(entry: str, hash: int) -> object:
    """
    Gets data from manifest
    """
    data = get_request_response(f"/Destiny2/Manifest/Destiny{entry}Definition/{hash}/", manifest=True)
    return data

def get_request_response_oauth(path: str, access_token: str, cache: bool = True) -> object:
    """
    Get response from GET request with OAuth requirement with access key and components
    """
    header = {**HEADER, **{"Authorization": "Bearer " + access_token}}
    data = do_retry_request(cache, True, ROOT + path, header)
    if "Response" not in data.json():
        return None
    return data.json()["Response"]

def data_incomplete() -> bool:
    """
    Checks if all weekly and daily data exists
    """
    if (not os.path.isdir(DATA_FOLDER) or
        not os.path.isfile(RESETS_FILE) or
        not os.path.isfile(GM_FILE) or
        not os.path.isfile(GM_DESTINATION_FILE) or
        not os.path.isfile(GM_WEAPON_FILE) or
        not os.path.isdir(EVERVERSE_FOLDER) or
        not os.path.isdir(RAID_DUNGEON_FOLDER) or
        not os.path.isdir(DAILY_REWARDS_FOLDER)):
        return True
    return False

def weekly_data_outdated() -> bool:
    """
    Checks if weekly reset has been passed,
    signalling that all data is outdated
    """
    resets_data = read_data_file(RESETS_FILE)
    if not resets_data:
        return True
    weekly_reset_time = datetime.fromisoformat(resets_data["weeklyReset"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > weekly_reset_time:
        return True
    return False

def daily_data_outdated() -> bool:
    """
    Checks if daily reset has been passed,
    signaling that only daily data needs to be refreshed
    """
    resets_data = read_data_file(RESETS_FILE)
    if not resets_data:
        return True
    daily_reset_time = datetime.fromisoformat(resets_data["dailyReset"].replace("Z", "+00:00"))
    if datetime.now(timezone.utc) > daily_reset_time:
        return True
    return False

def setup_destiny_data() -> bool:
    """
    Setup weekly Destiny json data (daily in the case of eververse).
    Returns boolean indicating if successful or not
    """
    timestamp_print("Setting up destiny data...")

    incomplete = data_incomplete()
    weekly_reset = weekly_data_outdated()
    daily_reset = daily_data_outdated()

    if incomplete:
        timestamp_print("  Destiny data is incomplete")
    elif weekly_reset:
        timestamp_print("  New weekly data needs fetching")
    elif daily_reset:
        timestamp_print("  New daily data needs fetching")
    else:
        timestamp_print("  Reusing stored data")

    if incomplete or weekly_reset or daily_reset:
        #some data refresh needed
        m_type = get_key(".env", "MEMBERSHIP_TYPE")
        m_id = get_key(".env", "MEMBERSHIP_ID")
        ch_ids = {
            "hunter": get_key(".env", "HUNTER_ID"),
            "warlock": get_key(".env", "WARLOCK_ID"),
            "titan": get_key(".env", "TITAN_ID")
        }

        reset_data = read_data_file(RESETS_FILE)
        if not reset_data:
            reset_data = {
                "weeklyReset": "",
                "dailyReset": "",
                "currentDateWeekly": "",
                "currentDateDaily": ""
            }

        #check valid refresh key exist else create new one to get access key
        timestamp_print("  Acquiring access token...")
        if not check_refresh_token():
            auth_key = get_oauth_code()
            access_token = get_set_oauth(auth_key)
        else:
            access_token = get_set_oauth()
        if access_token is None:
            timestamp_print("    Failed getting access token")
            return False
        timestamp_print("    Access token acquired")

        timestamp_print("Gathering data from Bungie.Net API:")

        # DAILY RESET OR INCOMPLETE BELOW

        #clear daily rewards folder
        if os.path.isdir(DAILY_REWARDS_FOLDER):
            shutil.rmtree(DAILY_REWARDS_FOLDER)
            os.mkdir(DAILY_REWARDS_FOLDER)
        #daily playlist rewards
        timestamp_print("  Getting daily rewards:")
        visited_item_hashes = [] #keep track to avoid duplicates
        daily_activity_data_list = [] #to be reused for weekly gm
        for key, ch_id in ch_ids.items():
            timestamp_print(f"    {key.title()}...")
            character_data = get_request_response_oauth(f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/"
                                                        f"?components={component_types['CharacterActivities']}", access_token, False)
            activities = character_data["activities"]["data"]["availableActivities"]
            rewarding_activities = list(filter(lambda x: len(x["visibleRewards"]) > 0, activities)) #only check activities with rewards

            for activity in rewarding_activities:
                for reward in activity["visibleRewards"]:
                    if reward["rewardItems"][0]["uiStyle"] == "daily_grind_guaranteed":
                        #save daily item activity and item data
                        activity_hash = activity["activityHash"]
                        item_hash = reward["rewardItems"][0]["itemQuantity"]["itemHash"]
                        if item_hash in visited_item_hashes:
                            continue

                        visited_item_hashes.append(item_hash)
                        activity_data = get_manifest_data("Activity", activity_hash)
                        item_data = get_manifest_data("InventoryItem", item_hash)

                        daily_activity_data_list.append((activity, activity_data))
                        daily_reward_data = {
                            "item": item_data,
                            "source": activity_data
                        }
                        write_data_file(daily_reward_data, os.path.join(DAILY_REWARDS_FOLDER, str(item_hash) + ".json"))
                        break

        #clear eververse folder
        if os.path.isdir(EVERVERSE_FOLDER):
            shutil.rmtree(EVERVERSE_FOLDER)
            os.mkdir(EVERVERSE_FOLDER)
        #eververse dailies
        timestamp_print("  Getting eververse:")
        gathered = [] #keep track of item hashes to ignore shared items
        for key, ch_id in ch_ids.items():
            timestamp_print(f"    {key.title()}...")
            for vendor_hash in eververse_vendors:
                #get vendor data
                eververse_data = get_request_response_oauth(f"/Destiny2/{m_type}/Profile/{m_id}/Character/{ch_id}/Vendors/{vendor_hash}/" +
                                    f"?components={component_types['VendorCategories']}," +
                                    f"{component_types['VendorSales']}", access_token, False)
                #write each item's data to a file
                categories = eververse_data["categories"]["data"]["categories"]
                for category in categories:
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

        #reset.json daily reset, for checking if up to date in the future
        daily_end_date = item["overrideNextRefreshDate"]
        reset_data["dailyReset"] = daily_end_date
        reset_data["currentDateDaily"] = (datetime.fromisoformat(daily_end_date) - timedelta(days=1)).isoformat(timespec="seconds")

        # WEEKLY RESET OR INCOMPLETE BELOW

        if incomplete or weekly_reset:
            #weekly grandmaster vanguard alert
            timestamp_print("  Getting grandmaster...")
            found = False
            for (activity, activity_data) in daily_activity_data_list: #activities with daily farmable weapon (includes gm)
                if "difficultyTierCollectionHash" not in activity_data:
                    continue
                difficulty_hash = activity_data["difficultyTierCollectionHash"]
                if str(difficulty_hash) == hashes["GMAlertDifficulty"]:
                    gm = activity
                    gm_data = activity_data
                    found = True
                    timestamp_print("    Found!")
                    write_data_file(gm_data, GM_FILE)
                    break

            if not found: #gm not found
                timestamp_print("    Not found")
                write_data_file({}, GM_FILE)
                write_data_file({}, GM_DESTINATION_FILE)
                write_data_file({}, GM_WEAPON_FILE)
            else:
                #gm alert destination
                timestamp_print("  Getting gm destination...")
                destination_data = get_manifest_data("Destination", gm_data["destinationHash"])
                write_data_file(destination_data, GM_DESTINATION_FILE)

                #featured gm weapon
                timestamp_print("  Getting gm weapon...")
                weapon_hash = gm["visibleRewards"][0]["rewardItems"][0]["itemQuantity"]["itemHash"]
                weapon_data = get_manifest_data("InventoryItem", weapon_hash)
                write_data_file(weapon_data, GM_WEAPON_FILE)

            #clear featured folder
            if os.path.isdir(RAID_DUNGEON_FOLDER):
                shutil.rmtree(RAID_DUNGEON_FOLDER)
                os.mkdir(RAID_DUNGEON_FOLDER)
            #raids and dungeons
            timestamp_print("  Getting raids and dungeons...")
            for activity in activities:
                if "challenges" not in activity: #this fails if you have completed the featured already
                    continue
                activity_hash = activity["activityHash"]
                activity_data = get_manifest_data("Activity", activity_hash)
                activity_type_hash = activity_data["activityTypeHash"]
                if str(activity_type_hash) in [hashes["Raid"], hashes["Dungeon"]]:
                    if ((("selectionScreenDisplayProperties" in activity_data and activity_data["selectionScreenDisplayProperties"]["name"] != "Master") or
                        "selectionScreenDisplayProperties" not in activity_data) and
                        "(Epic)" not in activity_data["displayProperties"]["name"]): #filter out master and epic versions of raids+dungeons
                        #get destination info and add into activity data
                        destination_data = get_manifest_data("Destination", activity_data["destinationHash"])
                        destination_name = destination_data["displayProperties"]["name"]
                        activity_data["destinationName"] = destination_name
                        write_data_file(activity_data, os.path.join(RAID_DUNGEON_FOLDER, f"{activity_hash}.json"))

            #reset.json weekly reset, for checking if up to date in the future
            timestamp_print("  Getting next weekly reset...")
            milestones_data = get_request_response("/Destiny2/Milestones/", False)
            first = list(milestones_data)[0]
            weekly_end_date = milestones_data[first]["endDate"]
            reset_data["weeklyReset"] = weekly_end_date
            reset_data["currentDateWeekly"] = (datetime.fromisoformat(weekly_end_date) - timedelta(weeks=1)).isoformat(timespec="seconds")

        #write next weekly and daily reset times to file
        write_data_file(reset_data, RESETS_FILE)

    timestamp_print("Done!")
    return True

def get_account_data(name: str, tag: int) -> object:
    """
    Gets account data from name and tag
    """
    info = {
        "displayName": name,
        "displayNameCode": tag
    }
    account_data = post_request_response("/Destiny2/SearchDestinyPlayerByBungieName/-1/", info)
    return account_data

def get_characters_data(type: int, id: str) -> object:
    """
    Gets the characters for a given account
    """
    response = get_request_response(f"/Destiny2/{type}/" +
                                    f"Profile/{id}/" +
                                    f"?components={component_types['Characters']}")
    if not response:
        return None
    return response["characters"]["data"]

def get_rarity_color(item: object) -> tuple[int, int, int]:
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
