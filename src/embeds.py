import os
import re
from datetime import datetime, timedelta, timezone
import src.destiny as destiny
from discord import Embed, Colour, ButtonStyle, Interaction
from discord.ui import View, Button, Select
from PIL import Image

class OwnedView(View):
    """
    View with stored owner
    """
    def __init__(self, owner_id):
        self.owner_id = owner_id
        super().__init__()

    #overwrite interaction check
    async def interaction_check(self, context: Interaction) -> bool:
        if self.owner_id == context.user.id:
            return True
        await context.response.send_message("You can't interact with this message!", ephemeral=True)
        return False

def get_gm_data_embeds() -> list[Embed]:
    """
    Gets formatted embeds with grandmaster nightfall data
    """
    embeds = []

    #data from grandmaster.json
    gm_data = destiny.read_data_file(destiny.GM_FILE)
    if gm_data:
        gm_name = gm_data["displayProperties"]["description"]
        gm_bg_url = destiny.IMG_ROOT + gm_data["pgcrImage"]

        #data from gm_destination.json
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
            .set_author(name="Nightfall: Grandmaster", icon_url=destiny.NIGHTFALL_URL)
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
    directory = os.listdir(destiny.GM_WEAPONS_FOLDER)
    for filename in directory:
        weapon_data = destiny.read_data_file(os.path.join(destiny.GM_WEAPONS_FOLDER, filename))
        weapon_name = weapon_data["displayProperties"]["name"]
        weapon_url = destiny.IMG_ROOT + weapon_data["displayProperties"]["icon"]
        weapon_description = weapon_data["flavorText"]
        embeds.insert(0,
            Embed(
                title=weapon_name,
                description=weapon_description
            )
            .set_author(name="Weekly Nightfall Weapon")
            .set_thumbnail(url=weapon_url)
        )
    return embeds

def get_pinnacle_data_embeds() -> list[Embed]:
    """
    Gets formatted embeds with all pinnacle raids and dungeons
    """
    #separate into raids and dungeons
    raids = []
    dungeons = []
    directory = os.listdir(destiny.RAID_DUNGEON_FOLDER)
    for filename in directory:
        file_data = destiny.read_data_file(os.path.join(destiny.RAID_DUNGEON_FOLDER, filename))
        if str(file_data["activityTypeHash"]) == destiny.hashes["Raid"]:
            raids.append(file_data)
        else:
            dungeons.append(file_data)
    #add each raid and dungeon embed
    embeds = []
    embeds.append(
        Embed().set_author(name="Weekly Pinnacle Raids and Dungeons")
    )
    activities = raids + dungeons
    for activity in activities:
        name = activity["originalDisplayProperties"]["name"]
        description = activity["originalDisplayProperties"]["description"]
        destination = activity["destinationName"]
        bg_url = destiny.IMG_ROOT + activity["pgcrImage"]
        #raid or dungeon
        activity_type = "Raid" if str(activity["activityTypeHash"]) == destiny.hashes["Raid"] else "Dungeon"
        activity_url = destiny.RAID_URL if str(activity["activityTypeHash"]) == destiny.hashes["Raid"] else destiny.DUNGEON_URL
        embeds.append(
            Embed(
                title=name,
                description=description
            )
            .set_author(name=activity_type, icon_url=activity_url)
            .set_image(url=bg_url)
            .set_footer(text=destination)
        )
    return embeds

def get_account_data_embeds_lookup(new_view: OwnedView, name: str, tag: int, type: int = None) -> tuple[list[Embed], OwnedView, int, str]:
    """
    Gets formatted embeds with account data from name and tag for lookup command
    Also returns membership type and id
    """
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
    else:
        display_name = account_data[0]["displayName"]
        membership_type = account_data[0]["membershipType"]
        membership_id = account_data[0]["membershipId"]

    bungie_display_name = account_data[0]["bungieGlobalDisplayName"]

    #create embed
    embeds = []
    embeds.append(
        Embed(
            title=f"{bungie_display_name}#{str(tag).zfill(4)}",
            description="Display Name: " + display_name
        )
        .set_author(name="User Lookup")
        .set_footer(text=f"Platform: {destiny.platforms[membership_type][0]}", icon_url=destiny.platforms[membership_type][1])
    )
    embeds.append(
        Embed(description="Loading characters...")
    )

    #create buttons view for each profile type
    view = new_view
    view.timeout = None
    for item in membership_types:
        if item == membership_type:
            button_style = ButtonStyle.primary
            disabled = True
        else:
            button_style = ButtonStyle.secondary
            disabled = False
        view.add_item(
            Button(
                style=button_style,
                label=destiny.platforms[item][0],
                custom_id=f"lookup%{name};{tag};{item}",
                disabled=disabled
            )
        )
    return embeds, view, membership_type, membership_id

def get_character_data_embeds(initial: list[Embed], type: int, id: str) -> list[Embed]:
    """
    Gets formatted embeds for character data for an account
    """
    embeds = [initial[0]]

    #get characters data
    characters_data = destiny.get_characters_data(type, id)
    if not characters_data:
        return embeds + [Embed(title="No characters found!")]

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

def get_loading_embed(command: str, name: str, tag: int = None):
    """
    Gets embed for loading for multiple commands
    """
    title = f"Searching For: {name}"
    if tag:
        title += "#" + str(tag).zfill(4)
    embed = Embed(
        title=title,
        description="Searching..."
    )
    if command == "topweapons":
        embed.set_author(name="Top Exotic Weapons")
    elif command in ["lookup", "search"]:
        embed.set_author(name="User lookup")
    elif command == "lastactivity":
        embed.set_author(name="Last activity")
    return embed

def get_search_embed(new_view: OwnedView, name: str, page: int) -> tuple[Embed, OwnedView]:
    """
    Gets embed for a page of user search results
    """
    #get search results
    payload = {
        "displayNamePrefix": name
    }
    search_data = destiny.post_request_response(f"/User/Search/GlobalName/{page}/", payload)
    if not search_data:
        return None, None
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
        title=f"Search Results For: {name}"
    )
    embed.set_author(name="User Lookup")
    i = 0
    for user in results:
        user_name = user["bungieGlobalDisplayName"]
        user_tag = user["bungieGlobalDisplayNameCode"]
        #translate platforms
        platforms = [destiny.platforms[m["membershipType"]][0] for m in user["destinyMemberships"]]
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
            label=f"{i}: {formatted_name}",
            value=f"{user_name};{formatted_tag};{first_platform}"
        )
        i += 1
    embed.set_footer(text=f"Page: {page + 1}")

    #build view
    view = new_view
    view.timeout = None
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

def get_eververse_data_embeds(new_view: OwnedView, category: str) -> tuple[list[Embed], OwnedView]:
    """
    Gets embeds for a selected category in eververse
    """
    embeds = []
    view = new_view
    view.timeout = None

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
        r, g, b = destiny.get_rarity_color(item_data)
        item_colour = Colour.from_rgb(r, g, b)

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
            disabled = True
        else:
            button_style = ButtonStyle.secondary
            disabled = False
        view.add_item(Button(
            style=button_style,
            label=existing + "s",
            custom_id="eververse%" + existing,
            disabled=disabled
        ))
    return embeds, view

def get_patches_data_embed(num_patches: int = 5) -> Embed:
    """
    Get embed for the past (default)5 patch notes
    """
    #get rss news articles filtered for patch notes
    patches_data = destiny.get_request_response("/Content/Rss/NewsArticles/0/?categoryfilter=updates")
    articles = [a for a in patches_data["NewsArticles"] if "Destiny 2" in a["Title"]]

    #create embed
    embed = Embed(
        title=f"Most Recent Destiny 2 Patch Notes",
        color=Colour.from_rgb(210, 119, 48)
    )
    image_url = articles[0]["ImagePath"]
    embed.set_image(url=image_url)

    #add articles to embed
    for article in articles[:num_patches]:
        title = article["Title"]
        link = destiny.IMG_ROOT + article["Link"]
        description = article["Description"]
        date = datetime.fromisoformat(article["PubDate"].replace("Z", "+00:00")).date()
        embed.add_field(
            name=f"{title}",
            value=f"{description}\n{date}: [Link to article]({link})",
            inline=False
        )
    return embed

def get_account_data_embeds_weapons(name: str, tag: int) -> tuple[list[Embed], object]:
    """
    Gets formatted embeds with account data from name and tag for top weapons command
    Also returns account object
    """
    #get account data
    account_data = destiny.get_account_data(name, tag)
    if not account_data:
        return None, None

    #keep track of which display names and platforms account has
    display_names = [m["displayName"] for m in account_data]
    platforms = [destiny.platforms[m["membershipType"]][0] for m in account_data]

    bungie_display_name = account_data[0]["bungieGlobalDisplayName"]

    #create embed
    embeds = []
    embeds.append(
        Embed(
            title=f"{bungie_display_name}#{str(tag).zfill(4)}"
        )
        .set_author(name="Top Exotic Weapons")
        .add_field(name="Display Names", value=", ".join(display_names), inline=False)
        .add_field(name="Platforms", value=", ".join(platforms), inline=False)
    )
    embeds.append(
        Embed(description="Loading top exotics...")
    )
    return embeds, account_data

def get_top_weapons_embeds(initial: list[Embed], accounts_data: object, amt: int = 3) -> list[Embed]:
    """
    Gets embed displaying the top 3 highest kill exotics for an account
    """
    embeds = [initial[0]]
    weapon_counts = {}

    #iterate through each character of each membership
    for account in accounts_data:
        membership_type = account["membershipType"]
        membership_id = account["membershipId"]
        response = destiny.get_characters_data(membership_type, membership_id)
        if not response:
            continue
        character_ids = list(response)
        for character_id in character_ids:
            stats = destiny.get_request_response(f"/Destiny2/{membership_type}/Account/{membership_id}/Character/{character_id}/Stats/UniqueWeapons/")
            if "weapons" not in stats:
                continue
            weapon_data = stats["weapons"]
            #add kill count to tally
            for weapon in weapon_data:
                weapon_id = weapon["referenceId"]
                weapon_kills = weapon["values"]["uniqueWeaponKills"]["basic"]["value"]
                if weapon_id in weapon_counts:
                    weapon_counts[weapon_id] += weapon_kills
                else:
                    weapon_counts[weapon_id] = weapon_kills

    if not weapon_counts:
        return embeds + [Embed(title="No weapon data found!")]

    #sort and get the top
    weapon_counts_list = list(weapon_counts.items())
    weapon_counts_list.sort(key=lambda e: e[1], reverse=True)
    top = weapon_counts_list[:amt]

    #create embeds
    pos = 1
    for weapon in top:
        weapon_hash = weapon[0]
        weapon_kills = int(weapon[1])

        #get weapon data
        weapon_data = destiny.get_manifest_data("InventoryItem", weapon_hash)
        weapon_name = weapon_data["displayProperties"]["name"]
        weapon_url = destiny.IMG_ROOT + weapon_data["displayProperties"]["icon"]
        weapon_flavortext = weapon_data["flavorText"]
        #rarity color
        r, g, b = destiny.get_rarity_color(weapon_data)
        rarity_colour = Colour.from_rgb(r, g, b)

        #add embed
        embeds.append(
            Embed(
                title=weapon_name,
                description=weapon_flavortext,
                color=rarity_colour
            )
            .set_author(name=f"#{pos}")
            .set_thumbnail(url=weapon_url)
            .add_field(name="Kills", value=str(weapon_kills))
        )
        pos += 1
    return embeds

def get_account_data_embeds_activity(name: str, tag: int) -> tuple[list[Embed], object]:
    """
    Gets formatted embeds with account data from name and tag for last activity command
    Also returns account object
    """
    #get account data
    account_data = destiny.get_account_data(name, tag)
    if not account_data:
        return None, None

    bungie_display_name = account_data[0]["bungieGlobalDisplayName"]

    #keep track of which display names and platforms account has
    display_names = [m["displayName"] for m in account_data]
    platforms = [destiny.platforms[m["membershipType"]][0] for m in account_data]

    #create embed
    embeds = []
    embeds.append(
        Embed(
            title=f"{bungie_display_name}#{str(tag).zfill(4)}"
        )
        .set_author(name="Last Activity")
        .add_field(name="Display Names", value=", ".join(display_names), inline=False)
        .add_field(name="Platforms", value=", ".join(platforms), inline=False)
    )
    embeds.append(
        Embed(description="Loading last activity...")
    )
    return embeds, account_data

def get_last_activity_embeds(initial: list[Embed], accounts_data: object) -> list[Embed]:
    """
    Gets embed with stats and information of an accounts most recent activity
    """
    embeds = [initial[0]]
    activities = []

    #get last activity for each character on each account
    for account in accounts_data:
        membership_type = account["membershipType"]
        membership_id = account["membershipId"]
        response = destiny.get_characters_data(membership_type, membership_id)
        if not response:
            continue
        character_ids = list(response)
        for character_id in character_ids:
            activities_data = destiny.get_request_response(f"/Destiny2/{membership_type}/Account/{membership_id}/Character/{character_id}/Stats/Activities/" +
                                                    f"?count=1&mode=7&page=0", False) #for now only pve (mode=7)
            if not activities_data or not activities_data["activities"]:
                continue
            reference_id = int(activities_data["activities"][0]["activityDetails"]["instanceId"])
            activity_report = destiny.get_request_response(f"/Destiny2/Stats/PostGameCarnageReport/{reference_id}/")
            activities.append(activity_report)

    #get last activity
    activities.sort(key=lambda a: datetime.fromisoformat(a["period"].replace("Z", "+00:00")), reverse=True)
    if not activities:
        return embeds + [Embed(title="No activities found!")]
    recent_activity = activities[0]

    #get activity data
    activity_time = datetime.fromisoformat(recent_activity["period"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    time_since_played = format_timedelta(now - activity_time)

    activity_hash = recent_activity["activityDetails"]["directorActivityHash"]
    activity_data = destiny.get_manifest_data("Activity", activity_hash)
    activity_name = activity_data["displayProperties"]["name"]
    activity_description = activity_data["displayProperties"]["description"]
    activity_image_url = destiny.IMG_ROOT + activity_data["pgcrImage"]

    destination_data = destiny.get_manifest_data("Destination", activity_data["destinationHash"])
    dest_name = destination_data["displayProperties"]["name"]

    #create activity embed
    embeds.append(Embed(
            title=activity_name,
            description=activity_description
        )
        .add_field(name=("Started from beginning " if recent_activity["activityWasStartedFromBeginning"]
                        else "Started from checkpoint ") + time_since_played + " ago",
            value="", inline=False)
        .set_image(url=activity_image_url)
        .set_footer(text=dest_name)
    )

    #sort list of players by score, or kills if no score
    players = recent_activity["entries"]
    if sum(p["score"]["basic"]["value"] for p in players) == 0:
        players.sort(key=lambda p: p["values"]["kills"]["basic"]["value"], reverse=True)
    else:
        players.sort(key=lambda p: p["score"]["basic"]["value"], reverse=True)
    players = players[:8] #max 10 embeds in a message
    activity_completed = 0.0 #see if any player completed activity

    for player in players:
        #player info
        guardian_class = player["player"]["characterClass"]
        power = player["player"]["lightLevel"]
        platform_type = player["player"]["destinyUserInfo"]["membershipType"]
        display_name = player["player"]["destinyUserInfo"]["displayName"]
        name = player["player"]["destinyUserInfo"]["bungieGlobalDisplayName"]
        tag = str(player["player"]["destinyUserInfo"]["bungieGlobalDisplayNameCode"]).zfill(4)

        #emblem
        emblem_url = destiny.IMG_ROOT + player["player"]["destinyUserInfo"]["iconPath"]
        emblem_hash = player["player"]["emblemHash"]
        emblem_data = destiny.get_manifest_data("InventoryItem", emblem_hash)
        emblem_bg_url = destiny.IMG_ROOT + emblem_data["secondarySpecial"]

        #copy emblem color
        r = emblem_data["backgroundColor"]["red"]
        g = emblem_data["backgroundColor"]["green"]
        b = emblem_data["backgroundColor"]["blue"]

        #player stats
        completed = player["values"]["completed"]["basic"]["value"]
        score = player["score"]["basic"]["displayValue"]
        kills = int(player["values"]["kills"]["basic"]["value"])
        assists = int(player["values"]["assists"]["basic"]["value"])
        deaths = int(player["values"]["deaths"]["basic"]["value"])
        kdr = player["values"]["killsDeathsRatio"]["basic"]["displayValue"]
        time_played = player["values"]["timePlayedSeconds"]["basic"]["displayValue"]

        activity_completed += completed

        #create player embed
        embed = Embed(
            title=display_name,
            description=f"{power} {guardian_class}",
            color=Colour.from_rgb(r, g, b)
        )
        embed.set_author(name=f"{name}#{tag}")
        embed.set_thumbnail(url=emblem_url)
        embed.set_image(url=emblem_bg_url)
        embed.set_footer(text=destiny.platforms[platform_type][0], icon_url=destiny.platforms[platform_type][1])

        #add stat fields
        embed.add_field(name="Kills", value=str(kills + assists))
        embed.add_field(name="Deaths", value=str(deaths))
        embed.add_field(name="K/D", value=kdr)
        embed.add_field(name="Final Blows", value=str(kills))
        embed.add_field(name="Score", value=score)
        embed.add_field(name="Time Played", value=time_played)

        if not completed: #mark as not completed
            embed.color = Colour.from_rgb(240, 77, 66)
            embed.add_field(name="Did not complete", value="", inline=False)
        embeds.append(embed)

    #mark activity as not completed if no player completed
    if not activity_completed:
        embeds[1].color = Colour.from_rgb(240, 77, 66)
        embeds[1].add_field(name="Did not complete", value="", inline=False)
    return embeds

def format_timedelta(time: timedelta) -> str:
    """
    Formats a timedelta object for pretty printing
    """
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