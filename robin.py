from dotenv import get_key
import asyncio
from src.destiny import (
    setup_destiny_data,
)
from src.embeds import (
    OwnedView,
    get_account_data_embeds_lookup,
    get_character_data_embeds,
    get_search_embed,
    get_search_loading_embed,
    get_gm_data_embeds,
    get_eververse_data_embeds,
    get_pinnacle_data_embeds,
    get_patches_data_embed,
    get_account_data_embeds_weapons,
    get_top_weapons_embeds
)
import discord

API_KEY = get_key(".env", "DISCORD_API_KEY")

#setup destiny data
if not setup_destiny_data():
    exit(-1)

#start discord bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print("Robin D. Estiny: Running!")

#helper functions ---------------------------------------------------------
async def handle_eververse(first: bool, context: discord.Interaction, arg: str = None):
    """
    Responds with embeds and view from eververse creator and sets callbacks for buttons
    """
    embeds, view = get_eververse_data_embeds(context, arg)
    for button in view.children:
        button.callback = action_callback
    if first:
        await context.response.send_message(embeds=embeds, view=view)
    else:
        await context.response.edit_message(embeds=embeds, view=view)

async def handle_character_lookup(first: bool, context: discord.Interaction, embeds_initial: list[discord.Embed], view: OwnedView, type: int, id: str):
    """
    Handles lookup response after account data and embed has been gathered
    """
    for button in view.children:
        button.callback = action_callback
    if first:
        await context.response.send_message(embeds=embeds_initial)
    else:
        await context.response.edit_message(embeds=embeds_initial, view=None)
    embeds_full = get_character_data_embeds(embeds_initial, type, id)
    await context.edit_original_response(embeds=embeds_full, view=view)

async def handle_search(first: bool, context: discord.Interaction, name: str, page: int = 0):
    """
    Handles the page scrolling etc of the user search
    """
    loading_embed = get_search_loading_embed(name, page)
    #loading to make command not time out
    if first:
        await context.response.send_message(embed=loading_embed, ephemeral=True)
    else:
        #save old message contents in case search fails
        original_embed = context.message.embeds[0]
        original_view = OwnedView(context.user.id)
        for comp in discord.ui.view._walk_all_components(context.message.components):
            original_view.add_item(discord.ui.view._component_to_item(comp))
        await context.response.edit_message(embed=loading_embed, view=None)
    #actual response
    embed, view = get_search_embed(context, name, page)
    attempts = 0
    while embed is None and attempts < 5: #search fails for some reason
        attempts += 1
        embed, view = get_search_embed(context, name, page)
        await asyncio.sleep(2)
    if not first and embed is None:
        await context.edit_original_response(embed=original_embed, view=original_view)
        return
    #response found
    hook = context.followup
    if first and embed is None:
        await context.delete_original_response() #delete first loading ephemeral message
        await hook.send("No users found!", ephemeral=True)
    else:
        for action in view.children:
            action.callback = action_callback
        if first:
            await context.delete_original_response() #delete first loading ephemeral message
            await hook.send(embed=embed, view=view)
        else:
            await context.edit_original_response(embed=embed, view=view)

#--------------------------------------------------------------------------
async def action_callback(context: discord.Interaction):
    contents = context.data["custom_id"].split("%", 1)
    if contents[0] == "lookup": #user lookup
        if contents[1]: #from lookup response
            splitted = contents[1].split(";")
        else: #from search dropdown
            splitted = context.data["values"][0].split(";")
        name = splitted[0]
        tag = splitted[1]
        type = int(splitted[2])
        embeds_initial, view, type, id = get_account_data_embeds_lookup(context, name, tag, type)
        await handle_character_lookup(False, context, embeds_initial, view, type, id)
    elif contents[0] == "search": #user search
        splitted = contents[1].split(";")
        name = splitted[0]
        page = int(splitted[1])
        await handle_search(False, context, name, page)
    elif contents[0] == "eververse": #eververse
        await handle_eververse(False, context, contents[1])
    else:
        pass

#--------------------------------------------------------------------------
@tree.command(
    name="eververse",
    description="Get all weekly bright dust offers from eververse"
)
async def eververse(context: discord.Interaction):
    await handle_eververse(True, context)

#--------------------------------------------------------------------------
@tree.command(
    name="gm",
    description="Get information about the current active grandmaster nightfall"
)
async def gm(context: discord.Interaction):
    embeds = get_gm_data_embeds()
    await context.response.send_message(embeds=embeds)

#--------------------------------------------------------------------------
@tree.command(
    name="pinnacle",
    description="Get all weekly pinnacle raids and dungeons"
)
async def pinnacle(context: discord.Interaction):
    embeds = get_pinnacle_data_embeds()
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
        await handle_search(True, context, name)
    else:
        embeds_initial, view, type, id = get_account_data_embeds_lookup(context, name, str(tag))
        if embeds_initial is None:
            await context.response.send_message("User was not found!", ephemeral=True)
        else:
            await handle_character_lookup(True, context, embeds_initial, view, type, id)

#--------------------------------------------------------------------------
@tree.command(
    name="topweapons",
    description="Get the top exotic weapons for a destiny account"
)
@discord.app_commands.describe(
    name="Destiny username",
    tag="The four digits after the '#'"
)
async def topweapons(context: discord.Interaction, name: str, tag: int):
    embeds_initial, account_data = get_account_data_embeds_weapons(name, str(tag))
    if embeds_initial is None:
        await context.response.send_message("User was not found!", ephemeral=True)
    else:
        await context.response.send_message(embeds=embeds_initial)
        embeds_full = get_top_weapons_embeds(embeds_initial, account_data)
        await context.edit_original_response(embeds=embeds_full)

#--------------------------------------------------------------------------
@tree.command(
    name="patches",
    description="See the past few Destiny 2 patch notes"
)
async def patches(context: discord.Interaction):
    embed = get_patches_data_embed()
    await context.response.send_message(embed=embed)

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
        .add_field(name="/gm", value="Get information about the current active grandmaster nightfall", inline=False)
        .add_field(name="/pinnacle", value="See the weekly pinnacle raids and dungeons", inline=False)
        .add_field(name="/eververse", value="Browse through all the weekly bright dust offerings in Eververse", inline=False)
        .add_field(name="/lookup", value="Find a Destiny account and all of their guardians", inline=False)
        .add_field(name="/topweapons", value="Get the most used exotic weapons of a Destiny player", inline=False)
        .add_field(name="/patches", value="Get the most recent Destiny 2 patch notes", inline=False)
    )

if __name__ == "__main__":
    print("Starting...")
    client.run(API_KEY)
