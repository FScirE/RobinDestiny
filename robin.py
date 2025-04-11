from dotenv import get_key
from destiny import (
    setup_destiny_data, 
    read_data_file
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
    print("Robin D. Estiny: Ready!")

@tree.command(
    name="gm", 
    description="Get information about the current active grandmaster nightfall"
)
async def gm(context):
    data = read_data_file("data/grandmaster.json")
    await context.response.send_message(data)

@tree.command(
    name="robin", 
    description=f"See all the things you can do with Robin D. Estiny"
)
async def robin(context):
    await context.response.send_message(discord.Embed(
            title="Commands",
            description="All the commands that Robin D. Estiny provides"
        )
        .add_field(name="/gm", value="Get information about the current active grandmaster nightfall")
        .add_field(name="/example", value="Example")
    )

#run bot
client.run(API_KEY)
