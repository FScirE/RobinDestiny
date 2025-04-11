from dotenv import get_key
from destiny import setup_destiny_data

API_KEY = get_key("./.env", "DISCORD_APY_KEY")

setup_destiny_data()
