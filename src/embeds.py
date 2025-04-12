from datetime import datetime, timedelta, timezone
import src.destiny as destiny
from discord import Embed, Colour

"""
Gets formatted embeds with grandmaster nightfall data
"""
def get_gm_data_embeds():
    return None

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
                                            f"?components={destiny.component_types['Characters']}"
                                            )
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
        emblem_data = destiny.get_request_response(f"/Destiny2/Manifest/DestinyInventoryItemDefinition/{emblem_hash}/")
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