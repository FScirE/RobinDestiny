from dotenv import get_key
import asyncio
import threading
import schedule
import time
from src.destiny import (
    setup_destiny_data,
)
from src.embeds import (
    OwnedView,
    get_account_data_embeds_lookup,
    get_character_data_embeds,
    get_search_embed,
    get_loading_embed,
    get_gm_data_embeds,
    get_eververse_data_embeds,
    get_featured_data_embeds,
    get_account_data_embeds_weapons,
    get_top_weapons_embeds,
    get_account_data_embeds_activity,
    get_last_activity_embeds
)
from src.io import timestamp_print
import discord

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

API_KEY = get_key(".env", "DISCORD_API_KEY")

#start discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    timestamp_print("Robin D. Estiny: Running!")

#helper functions ---------------------------------------------------------
async def loading_search_command_wrapper(first: bool, context: discord.Interaction, command: str, name: str, tag: int = None):
    """
    Handles initial search in progress message and original message retention
    for commands using user search
    """
    loading_embed = await asyncio.to_thread(get_loading_embed, command, name, tag)
    original_embeds = None
    original_view = None
    #loading to make command not time out
    if first:
        await context.response.send_message(embed=loading_embed)
    else:
        #save old message contents in case lookup fails
        original_embeds = context.message.embeds
        original_view = OwnedView(context.user.id)
        for comp in discord.ui.view._walk_all_components(context.message.components):
            original_view.add_item(discord.ui.view._component_to_item(comp))
        await context.response.edit_message(embed=loading_embed, view=None)
    return original_embeds, original_view

#command handler functions ------------------------------------------------
async def handle_eververse(first: bool, context: discord.Interaction, arg: str = None):
    """
    Responds with embeds and view from eververse creator and sets callbacks for buttons
    """
    new_view = OwnedView(context.user.id)
    embeds, view = await asyncio.to_thread(get_eververse_data_embeds, new_view, arg)
    for button in view.children:
        button.callback = action_callback
    if first:
        await context.response.send_message(embeds=embeds, view=view)
    else:
        await context.response.edit_message(embeds=embeds, view=view)

async def handle_top_weapons(first: bool, context: discord.Interaction, name: str, tag: int):
    """
    Handles response for top weapon lookup
    """
    #loading to make command not time out
    original_embeds, original_view = await loading_search_command_wrapper(first, context, "topweapons", name, tag)
    #actual response
    embeds_initial, account_data = await asyncio.to_thread(get_account_data_embeds_weapons, name, tag)
    if not first and embeds_initial is None:
        await context.edit_original_response(embeds=original_embeds, view=original_view)
        return
    if embeds_initial is None:
        await context.delete_original_response()
        await context.followup.send("User was not found!", ephemeral=True)
    else:
        await context.edit_original_response(embeds=embeds_initial)
        embeds_full = await asyncio.to_thread(get_top_weapons_embeds, embeds_initial, account_data)
        await context.edit_original_response(embeds=embeds_full)

async def handle_last_activity(first: bool, context: discord.Interaction, name: str, tag: int):
    """
    Handles response for last activity lookup for specific user
    """
    #loading to make command not time out
    original_embeds, original_view = await loading_search_command_wrapper(first, context, "lastactivity", name, tag)
    #actual response
    new_view = OwnedView(context.user.id)
    embeds_initial, view, account_data = await asyncio.to_thread(get_account_data_embeds_activity, new_view, name, tag)
    if not first and embeds_initial is None:
        await context.edit_original_response(embeds=original_embeds, view=original_view)
        return
    #response found
    if embeds_initial is None:
        await context.delete_original_response()
        await context.followup.send("User was not found!", ephemeral=True, wait=True)
    else:
        for action in view.children:
            action.callback = action_callback
        await context.edit_original_response(embeds=embeds_initial, view=None)
        embeds_full = await asyncio.to_thread(get_last_activity_embeds, embeds_initial, account_data)
        await context.edit_original_response(embeds=embeds_full, view=view)

async def handle_account_character_lookup(first: bool, context: discord.Interaction, name: str, tag: int, type: int):
    """
    Handles response for account and characters lookup
    """
    #loading to make command not time out
    original_embeds, original_view = await loading_search_command_wrapper(first, context, "lookup", name, tag)
    #actual response
    new_view = OwnedView(context.user.id)
    embeds_initial, view, type, id = await asyncio.to_thread(get_account_data_embeds_lookup, new_view, name, tag, type)
    if not first and embeds_initial is None:
        await context.edit_original_response(embeds=original_embeds, view=original_view)
        return
    #response found
    if embeds_initial is None:
        await context.delete_original_response()
        await context.followup.send("User was not found!", ephemeral=True, wait=True)
    else:
        for action in view.children:
            action.callback = action_callback
        await context.edit_original_response(embeds=embeds_initial, view=None)
        embeds_full = await asyncio.to_thread(get_character_data_embeds, embeds_initial, type, id)
        await context.edit_original_response(embeds=embeds_full, view=view)

async def handle_search(first: bool, context: discord.Interaction, name: str, page: int = 0, source: str = "lookup"):
    """
    Handles the page scrolling etc of the user search
    """
    #loading to make command not time out
    original_embeds, original_view = await loading_search_command_wrapper(first, context, source, name)
    #actual response
    new_view = OwnedView(context.user.id)
    embed, view = await asyncio.to_thread(get_search_embed, new_view, name, page, source)
    if not first and embed is None:
        await context.edit_original_response(embeds=original_embeds[0], view=original_view)
        return
    #response found
    if embed is None:
        await context.delete_original_response()
        await context.followup.send("No users found!", ephemeral=True)
    else:
        for action in view.children:
            action.callback = action_callback
        await context.edit_original_response(embed=embed, view=view)

#--------------------------------------------------------------------------
async def action_callback(context: discord.Interaction):
    #context formatted as [type]%[data];[data];... etc
    contents = context.data["custom_id"].split("%", 1)
    if contents[0] == "eververse": #eververse
        await handle_eververse(False, context, contents[1])
    elif contents[0] == "lookup": #user lookup
        if contents[1]: #from lookup response
            splitted = contents[1].split(";")
        else: #from search dropdown
            splitted = context.data["values"][0].split(";")
        name = splitted[0]
        tag = int(splitted[1])
        type = int(splitted[2])
        await handle_account_character_lookup(False, context, name.lower(), tag, type)
    elif contents[0] == "search": #user search
        splitted = contents[1].split(";")
        name = splitted[0]
        page = int(splitted[1])
        source = splitted[2]
        await handle_search(False, context, name.lower(), page, source)
    elif contents[0] == "lastactivity": #last activity
        if contents[1]: #from lookup response
            splitted = contents[1].split(";")
        else: #from search dropdown
            splitted = context.data["values"][0].split(";")
        name = splitted[0]
        tag = int(splitted[1])
        await handle_last_activity(False, context, name, tag)
    elif contents[0] == "topweapons": #top weapons (from search dropdown)
        splitted = context.data["values"][0].split(";")
        name = splitted[0]
        tag = int(splitted[1])
        await handle_top_weapons(False, context, name, tag)
    else:
        pass

#--------------------------------------------------------------------------
@tree.command(
    name="eververse",
    description="Get all daily bright dust offers from eververse"
)
async def eververse(context: discord.Interaction):
    await handle_eververse(True, context)

#--------------------------------------------------------------------------
@tree.command(
    name="gm",
    description="Get information about the current active grandmaster vanguard alert"
)
async def gm(context: discord.Interaction):
    embeds = await asyncio.to_thread(get_gm_data_embeds)
    await context.response.send_message(embeds=embeds)

#--------------------------------------------------------------------------
@tree.command(
    name="featured",
    description="Get all weekly featured raids and dungeons"
)
async def featured(context: discord.Interaction):
    embeds = await asyncio.to_thread(get_featured_data_embeds)
    await context.response.send_message(embeds=embeds)

#--------------------------------------------------------------------------
@tree.command(
    name="lookup",
    description="Search for and get information about a Destiny account"
)
@discord.app_commands.describe(
    name="Destiny username",
    tag="The four digits after the '#'"
)
async def lookup(context: discord.Interaction, name: str, tag: int = None):
    if tag is None:
        await handle_search(True, context, name.lower())
    else:
        await handle_account_character_lookup(True, context, name.lower(), tag)

#--------------------------------------------------------------------------
@tree.command(
    name="topweapons",
    description="Get the top exotic weapons for a destiny account"
)
@discord.app_commands.describe(
    name="Destiny username",
    tag="The four digits after the '#'"
)
async def topweapons(context: discord.Interaction, name: str, tag: int = None):
    if tag is None:
        await handle_search(True, context, name.lower(), source="topweapons")
    else:
        await handle_top_weapons(True, context, name.lower(), tag)

#--------------------------------------------------------------------------
@tree.command(
    name="lastactivity",
    description="Get stats and information from last activity of a player"
)
@discord.app_commands.describe(
    name="Destiny username",
    tag="The four digits after the '#'"
)
async def lastactivity(context: discord.Interaction, name: str, tag: int = None):
    if tag is None:
        await handle_search(True, context, name.lower(), source="lastactivity")
    else:
        await handle_last_activity(True, context, name.lower(), tag)

#--------------------------------------------------------------------------
@tree.command(
    name="robin",
    description=f"See all the things you can do with Robin D. Estiny"
)
async def robin(context: discord.Interaction):
    await context.response.send_message(embed=discord.Embed(
            title="Commands",
        )
        .set_thumbnail(url=client.user.avatar.url)
        .add_field(name="/gm", value="Get information about the current active grandmaster vanguard alert", inline=False)
        .add_field(name="/featured", value="See the weekly featured raids and dungeons", inline=False)
        .add_field(name="/eververse", value="Browse through all the daily bright dust offerings in Eververse", inline=False)
        .add_field(name="/lookup", value="Find a Destiny account and all of their guardians", inline=False)
        .add_field(name="/topweapons", value="Get the most used exotic weapons of a Destiny player", inline=False)
        .add_field(name="/lastactivity", value="See stats and information about the last activity played by an account")
    )

if __name__ == "__main__":
    #setup destiny data
    if not setup_destiny_data():
        exit(-1)

    #run setup every hour to check for daily/weekly resets
    schedule.every().hour.at(":01").do(setup_destiny_data)
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

    #start bot
    timestamp_print("Starting...")
    client.run(API_KEY)
