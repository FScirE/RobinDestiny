import os
import re
from datetime import datetime, timedelta, timezone
import src.destiny as destiny
from discord import Embed, Colour, ButtonStyle, SelectOption
from discord.ui import View, Button, Select
from PIL import Image

"""
Gets formatted embeds with grandmaster nightfall data
"""
def get_gm_data_embeds() -> list[Embed]:
    embeds = []

    #data from grandmaster.json
    gm_data = destiny.read_data_file(destiny.GM_FILE)
    if gm_data:
        gm_name = gm_data["displayProperties"]["description"]
        gm_icon_url = destiny.IMG_ROOT + gm_data["displayProperties"]["icon"]
        gm_bg_url = destiny.IMG_ROOT + gm_data["pgcrImage"]

        #data from gmdestination.json
        destination_data = destiny.read_data_file(destiny.DESTINATION_FILE)
        dest_name = destination_data["displayProperties"]["name"]
        dest_description = destination_data["displayProperties"]["description"]

        #categorized modifiers
        surges = []
        threat = None
        overcharge = None
        other = []
        directory = os.listdir(destiny.MODIFIERS_FOLDER)
        for filename in directory:
            file_data = destiny.read_data_file(os.path.join(destiny.MODIFIERS_FOLDER, filename))
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

        #main nightfall embed
        embeds.append(
            Embed(
                title=gm_name,
                description=f"{dest_name}\n{dest_description}"
            )
            .set_author(name="Nightfall: Grandmaster", icon_url=gm_icon_url)
            .set_image(url=gm_bg_url)
        )

        #modifier embeds
        modifiers = surges + [overcharge] + [threat] + other
        for modifier in modifiers:
            if not modifier:
                continue
            modifier_name = modifier["displayProperties"]["name"]
            desc_raw = modifier["displayProperties"]["description"]
            modifier_url = destiny.IMG_ROOT + modifier["displayProperties"]["iconSequences"][0]["frames"][0]

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
    else:
        embeds.append(
            Embed(title="Grandmaster not found!")
        )

    #nightfall weapon embed
    weapon_data = destiny.read_data_file(destiny.GM_WEAPON_FILE)
    weapon_name = weapon_data["displayProperties"]["name"]
    weapon_url = destiny.IMG_ROOT + weapon_data["displayProperties"]["icon"]
    weapon_description = weapon_data["flavorText"]
    embeds.insert(0,
        Embed(
            title=weapon_name,
            description=weapon_description
        )
        .set_author(name="Weekly nightfall weapon")
        .set_thumbnail(url=weapon_url)
    )

    return embeds

"""
Gets formatted embed with account data from name and tag
Also returns membership type and id
"""
def get_account_data_embed(name: str, tag: int, type: int = None) -> tuple[Embed, View, int, str]:
    #get account data
    account_data = destiny.get_account_data(name, tag)
    if not account_data:
        return None, None, None, None

    #keep track of which account types exist
    membership_types = [m["membershipType"] for m in account_data]

    #select primary profile (either cross saved primary or first in list) if not predetermined
    if type or account_data[0]["crossSaveOverride"]:
        membership_type = account_data[0]["crossSaveOverride"] if not type else type
        for data in account_data:
            if data["membershipType"] == membership_type:
                display_name = data["displayName"]
                membership_id = data["membershipId"]
                membership_url = destiny.IMG_ROOT + data["iconPath"]
    else:
        display_name = account_data[0]["displayName"]
        membership_type = account_data[0]["membershipType"]
        membership_id = account_data[0]["membershipId"]
        membership_url = destiny.IMG_ROOT + account_data[0]["iconPath"]

    #create embed
    embeds = []
    embeds.append(
        Embed(
            title=f"{name}#{str(tag).zfill(4)}",
            description="Display name: " + display_name)
        .set_footer(text=f"Platform: {destiny.platforms[membership_type]}", icon_url=membership_url)
    )
    embeds.append(
        Embed(description="Loading characters...")
    )

    #create buttons view for each profile type
    view = View(timeout=None)
    for item in membership_types:
        if item == membership_type:
            button_style = ButtonStyle.primary
        else:
            button_style = ButtonStyle.secondary
        view.add_item(Button(
            style=button_style,
            label=destiny.platforms[item],
            custom_id=f"lookup%{name};{tag};{item}"
        ))
    return embeds, view, membership_type, membership_id

"""
Gets formatted embeds for character data for an account
"""
def get_character_data_embeds(initial: list[Embed], type: int, id: str) -> list[Embed]:
    embeds = [initial[0]]

    #get characters data
    response = destiny.get_request_response(f"/Destiny2/{type}/" +
                                            f"Profile/{id}/" +
                                            f"?components={destiny.component_types['Characters']}")
    if not response:
        return embeds + [Embed(title="No characters found!")]
    characters_data = response["characters"]["data"]

    #sort after playtime
    sorted_characters_data = sorted(
        characters_data.items(),
        key=lambda item : int(item[1]["minutesPlayedTotal"]),
        reverse=True
    )

    #start building embeds
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
Gets embed for a page of user search results
"""
def get_search_embed(name: str, page: int) -> tuple[Embed, View]:
    #get search results
    payload = {
        "displayNamePrefix": name
    }
    search_data = destiny.post_request_response(f"/User/Search/GlobalName/{page}/", payload)
    has_more = search_data["hasMore"]
    results = [s for s in search_data["searchResults"] if s["destinyMemberships"]][:25] #avoid overfill
    if not results:
        return None, None

    #for exact lookup
    dropdown = Select(
        placeholder="Exact user lookup",
        custom_id="lookup%"
    )

    #build embed
    embed = Embed(
        title=f"Search results for: {name}"
    )
    i = 0
    for user in results:
        user_name = user["bungieGlobalDisplayName"]
        user_tag = user["bungieGlobalDisplayNameCode"]
        #translate platforms
        platforms = [destiny.platforms[m["membershipType"]] for m in user["destinyMemberships"]]
        #values reused for dropdown
        formatted_tag = str(user_tag).zfill(4)
        formatted_name = f"{user_name}#{formatted_tag}"
        first_platform = str(user["destinyMemberships"][0]["membershipType"])
        embed.add_field(
            name=f"{i}: {formatted_name}",
            value=f"{', '.join(platforms)}",
            inline=True
        )
        dropdown.add_option(
            label=formatted_name,
            value=f"{user_name};{formatted_tag};{first_platform}"
        )
        i += 1
    embed.set_footer(text=f"Page: {page + 1}")

    #build view
    view = View(timeout=None)
    view.add_item(dropdown)
    if page > 0:
        view.add_item(
            Button(
                style=ButtonStyle.primary,
                label="< Previous page",
                custom_id=f"search%{name};{page - 1}"
            )
        )
    if has_more:
        view.add_item(
            Button(
                style=ButtonStyle.primary,
                label="Next page >",
                custom_id=f"search%{name};{page + 1}"
            )
        )
    return embed, view

"""
Gets embed for a selected category in eververse
"""
def get_eververse_data_embeds(category: str) -> tuple[list[Embed], View]:
    embeds = []
    view = View(timeout=None)

    #all available types of cosmetics
    available_categories = []

    #look through all items
    folder = os.listdir(destiny.EVERVERSE_FOLDER)
    for file in folder:
        item_data = destiny.read_data_file(os.path.join(destiny.EVERVERSE_FOLDER, file))
        item_type = item_data["itemTypeDisplayName"]

        if item_type not in available_categories:
            available_categories.append(item_type)

        if item_type != category:
            continue

        #item information
        item_name = item_data["displayProperties"]["name"]
        item_text = item_data["flavorText"]
        item_price = item_data["price"]
        if not item_text: #use description if no flavor text
            item_text = item_data["displayProperties"]["description"]
        item_path = destiny.IMG_ROOT + item_data["displayProperties"]["icon"]
        if "screenshot" in item_data:
            item_image = destiny.IMG_ROOT + item_data["screenshot"]
        else:
            item_image = None

        #rarity color
        rarity = item_data["inventory"]["tierTypeName"]
        if rarity == "Exotic":
            item_colour = Colour.from_rgb(205, 173, 54)
        elif rarity == "Legendary":
            item_colour = Colour.from_rgb(79, 54, 99)
        else:
            item_colour = Colour.from_rgb(86, 126, 157)

        #create embed
        embed = Embed(
            title=item_name,
            description=item_text,
            color=item_colour
        )
        embed.set_thumbnail(url=item_path)
        embed.set_footer(text=str(item_price), icon_url=destiny.BRIGHT_DUST_URL)
        if item_image:
            embed.set_image(url=item_image)
        embeds.append(embed)

    #insert header
    if category is None:
        eververse_header = Embed(title="Select Item Category")
    else:
        eververse_header = Embed(title=category + "s")
    eververse_header.set_author(name="Weekly Eververse Items")
    embeds.insert(0, eververse_header)

    #create buttons to change category
    for existing in available_categories:
        if category == existing:
            button_style = ButtonStyle.primary
        else:
            button_style = ButtonStyle.secondary
        view.add_item(Button(
            style=button_style,
            label=existing + "s",
            custom_id="eververse%" + existing
        ))
    return embeds, view

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