from dotenv import get_key
from src.destiny import (
    setup_destiny_data,
)
from src.embeds import (
    get_account_data_embed,
    get_character_data_embeds,
    get_gm_data_embeds
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

#-------------------------------------
@tree.command(
    name="gm",
    description="Get information about the current active grandmaster nightfall"
)
async def gm(context: discord.Interaction):
    embeds = get_gm_data_embeds()
    await context.response.send_message(embeds=embeds)

#-------------------------------------
@tree.command(
    name="lookup",
    description="Get information about a Destiny account"
)
@discord.app_commands.describe(
    name="Destiny username",
    tag="The four digits after the '#'"
)
async def lookup(context: discord.Interaction, name: str, tag: int):
    embed_initial, _type, _id = get_account_data_embed(name, str(tag))
    if embed_initial is None:
        await context.response.send_message("User was not found!", ephemeral=True)
    else:
        await context.response.send_message(content="Loading characters...", embed=embed_initial)
        embeds_full = get_character_data_embeds(embed_initial, _type, _id)
        if embeds_full is None:
            await context.edit_original_response(content="", embeds=[embed_initial, discord.Embed(title="No characters found!")])
        else:
            await context.edit_original_response(content="", embeds=embeds_full)

#-------------------------------------
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
        .add_field(name="/lookup [name] [tag]", value="Look up information of a destiny account", inline=False)
    )

if __name__ == "__main__":
    print("Starting...")
    client.run(API_KEY)
