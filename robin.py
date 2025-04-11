from dotenv import get_key
from destiny import (
    setup_destiny_data,
    read_data_file,
    get_character_data_account_embed
)
import discord

API_KEY = get_key("./.env", "DISCORD_API_KEY")

#setup destiny data
setup_destiny_data()

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
    data = read_data_file("data/grandmaster.json")
    gm_name = data["displayProperties"]["description"]
    await context.response.send_message(gm_name)

#-------------------------------------
@tree.command(
    name="lookup",
    description="Get information about a Destiny account"
)
@discord.app_commands.describe(
    name="Bungie username",
    tag="The four digits after the '#'"
)
async def lookup(context: discord.Interaction, name: str, tag: int):
    embeds = get_character_data_account_embed(name, str(tag))
    if embeds is None:
        await context.response.send_message("User was not found!", ephemeral=True)
    else:
        await context.response.send_message(embeds=embeds)

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
        .add_field(name="/lookup", value="Look up information of a destiny account", inline=False)
    )

if __name__ == "__main__":
    print("Starting...")
    client.run(API_KEY)
