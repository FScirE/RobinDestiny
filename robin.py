from dotenv import get_key
from src.destiny import (
    setup_destiny_data,
)
from src.embeds import (
    get_account_data_embed,
    get_character_data_embeds,
    get_search_embed,
    get_gm_data_embeds,
    get_eververse_data_embeds
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
"""
Responds with embeds and view from eververse creator and sets callbacks for buttons
"""
async def handle_eververse(first: bool, context: discord.Interaction, arg: str = None):
    embeds, view = get_eververse_data_embeds(arg)
    for button in view.children:
        button.callback = button_callback
    if first:
        await context.response.send_message(embeds=embeds, view=view)
    else:
        await context.response.edit_message(embeds=embeds, view=view)

"""
Handles lookup response after account data and embed has been gathered
"""
async def handle_character_lookup(first: bool, context: discord.Interaction, embeds_initial: list[discord.Embed], view: discord.ui.View, type: int, id: str):
    for button in view.children:
        button.callback = button_callback
    if first:
        await context.response.send_message(embeds=embeds_initial)
    else:
        await context.response.edit_message(embeds=embeds_initial, view=None)
    embeds_full = get_character_data_embeds(embeds_initial, type, id)
    await context.edit_original_response(embeds=embeds_full, view=view)

"""
Handles the page scrolling etc of the user search
"""
async def handle_search(first: bool, context: discord.Interaction, name: str, page: int = 0):
    embed, view = get_search_embed(name, page)
    if first and embed is None:
        await context.response.send_message("No users found!", ephemeral=True)
    else:
        for button in view.children:
            button.callback = button_callback
        if first:
            await context.response.send_message(embed=embed, view=view)
        else:
            await context.response.edit_message(embed=embed, view=view)

#--------------------------------------------------------------------------
async def button_callback(context: discord.Interaction):
    contents = context.data["custom_id"].split("%", 1)
    if contents[0] == "lookup": #user lookup
        splitted = contents[1].split(";")
        name = splitted[0]
        tag = splitted[1]
        type = int(splitted[2])
        embeds_initial, view, type, id = get_account_data_embed(name, tag, type)
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
        embeds_initial, view, type, id = get_account_data_embed(name, str(tag))
        if embeds_initial is None:
            await context.response.send_message("User was not found!", ephemeral=True)
        else:
            await handle_character_lookup(True, context, embeds_initial, view, type, id)

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
        .add_field(name="/eververse", value="Browse through all the weekly bright dust offerings in Eververse", inline=False)
        .add_field(name="/lookup [name]", value="Search for Bungie accounts by name", inline=False)
        .add_field(name="/lookup [name] [tag]", value="Look up information of a Destiny account", inline=False)
    )

if __name__ == "__main__":
    print("Starting...")
    client.run(API_KEY)
