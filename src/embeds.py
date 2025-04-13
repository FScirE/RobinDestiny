import os
import re
from datetime import datetime, timedelta, timezone
import src.destiny as destiny
from discord import Embed, Colour

"""
Gets formatted embeds with grandmaster nightfall data
"""
def get_gm_data_embeds() -> list[Embed]:
    #data from grandmaster.json
    gm_data = destiny.read_data_file("data/grandmaster.json")
    gm_name = gm_data["displayProperties"]["description"]
    gm_icon_url = destiny.IMG_ROOT + gm_data["displayProperties"]["icon"]
    gm_bg_url = destiny.IMG_ROOT + gm_data["pgcrImage"]
    #data from gmdestination.json
    destination_data = destiny.read_data_file("data/gmdestination.json")
    dest_name = destination_data["displayProperties"]["name"]
    dest_description = destination_data["displayProperties"]["description"]

    #categorized modifiers
    surges = []
    threat = None
    overcharge = None
    other = []
    directory = os.listdir("data/gm_modifiers")
    for filename in directory:
        file_data = destiny.read_data_file(f"data/gm_modifiers/{filename}")
        modifier_name = file_data["displayProperties"]["name"].lower()
        if "surge" in modifier_name:
            file_data["positive"] = True
            surges.append(file_data)
        elif "overcharged" in modifier_name:
            file_data["positive"] = True
            overcharge = file_data
        elif "threat" in modifier_name:
            file_data["positive"] = False
            threat = file_data
        else:
            file_data["positive"] = False
            other.append(file_data)

    embeds = []
    #main nightfall embed
    embeds.append(
        Embed(
            title=gm_name,
            description=f"{dest_name}, {dest_description}"
        )
        .set_author(name="Nightfall: Grandmaster", icon_url=gm_icon_url)
        .set_image(url=gm_bg_url)
    )
    #modifier embeds
    modifiers = surges + [overcharge] + [threat] + other
    for modifier in modifiers:
        modifier_name = modifier["displayProperties"]["name"]
        desc_raw = modifier["displayProperties"]["description"]
        modifier_url = destiny.IMG_ROOT + modifier["displayProperties"]["icon"]

        #remove or replace variables
        modifier_desc = re.sub(r"\{[^\{\}]*\}", "25", desc_raw)
        modifier_desc = re.sub(r"\[[^\[\]]*\] ", "", modifier_desc)

        embed_colour = Colour.from_rgb(40, 138, 255) if modifier["positive"] else Colour.from_rgb(240, 77, 66)

        embeds.append(
            Embed(
                title=modifier_name,
                description=modifier_desc,
                color=embed_colour
            )
            .set_thumbnail(url=modifier_url)
        )
    return embeds

"""
Gets formatted embed with account data from name and tag
Also returns membership type and id
"""
def get_account_data_embed(name: str, tag: int) -> tuple[Embed, int, str]:
    #get account data
    account_data = destiny.get_account_data(name, tag)
    if not account_data:
        return None, None, None

    #select primary profile (either cross saved primary or first in list)
    if account_data[0]["crossSaveOverride"]:
        membership_type = account_data[0]["crossSaveOverride"]
        for data in account_data:
            if data["membershipType"] == membership_type:
                membership_id = data["membershipId"]
                membership_url = destiny.IMG_ROOT + data["iconPath"]
    else:
        membership_type = account_data[0]["membershipType"]
        membership_id = account_data[0]["membershipId"]
        membership_url = destiny.IMG_ROOT + account_data[0]["iconPath"]

    embed = Embed(title=f"{name}#{str(tag).zfill(4)}")
    embed.set_footer(text=f"Platform: {destiny.platforms[membership_type]}", icon_url=membership_url)
    return embed, membership_type, membership_id

"""
Gets formatted embeds for character data for an account
"""
def get_character_data_embeds(initial: Embed, type: int, id: str) -> list[Embed]:
    #get characters data
    response = destiny.get_request_response(f"/Destiny2/{type}/" +
                                            f"Profile/{id}/" +
                                            f"?components={destiny.component_types['Characters']}")
    if not response:
        return None
    characters_data = response["characters"]["data"]

    #sort after playtime
    sorted_characters_data = sorted(
        characters_data.items(),
        key=lambda item : int(item[1]["minutesPlayedTotal"]),
        reverse=True
    )

    #start building embeds
    embeds = [initial]
    for _, character in sorted_characters_data:
        minutes = int(character["minutesPlayedTotal"])
        guardian_class = destiny.classes[character["classHash"]]
        power = character["light"]
        emblem_url = destiny.IMG_ROOT + character["emblemPath"]

        #get emblem background
        emblem_hash = character["emblemHash"]
        emblem_data = destiny.get_manifest_data("InventoryItem", emblem_hash)
        emblem_bg_url = destiny.IMG_ROOT + emblem_data["secondarySpecial"]

        #copy emblem color
        r = character["emblemColor"]["red"]
        g = character["emblemColor"]["green"]
        b = character["emblemColor"]["blue"]

        #time since last played
        last = datetime.fromisoformat(character["dateLastPlayed"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        time_session = int(character["minutesPlayedThisSession"]) #minutes played can be !=0 despite no session being active
        session_start = now - timedelta(minutes=time_session)
        if not time_session or session_start > last:
            diff = format_timedelta(now - last)
        else:
            diff = "Now"

        embeds.append(
            Embed(
                title=f"{power} | {guardian_class}",
                #⣠⡾⠋⠙⢷⣄⣠⡾⠋⠙⢷⣄⣠⡾⠋⠙⢷⣄⣠⡾⠋⠙⢷⣄
                #description="\u28e0\u287e\u280b\u2819\u28B7\u28C4\u28e0\u287e\u280b\u2819\u28B7\u28C4\u28e0\u287e\u280b\u2819\u28B7\u28C4\u28e0\u287e\u280b\u2819\u28B7\u28C4",
                #description="\u2802"*24,
                color=Colour.from_rgb(r, g, b)
            )
            .add_field(name="Total time played", value=f"{minutes//60}h {minutes%60}m", inline=False)
            .add_field(name="Time since last played", value=diff, inline=False)
            .set_thumbnail(url=emblem_url)
            .set_image(url=emblem_bg_url)
        )
    return embeds

"""
Formats a datetime object for pretty printing
"""
def format_timedelta(time: timedelta) -> str:
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
    else:
        return_str += f"{minutes}m"

    return return_str