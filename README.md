# Robin D. Estiny
### A discord.py bot connected to the Bungie.Net API

## Features:
- Finding players by Bungie name
- Getting specific player information about their characters and platforms
- Getting a players most used exotic weapons
- Gathering stats and information about a players most recent (non-PvP, non-patrol) activity
- Seeing weekly grandmaster alert information
- Getting weekly grandmaster alert weapon
- Seeing the weekly pinnacle raids and dungeons
- Browsing all weekly bright dust items from Eververse

## Python packages required (Pip)
<b>Python 3.9></b>
- discord
- dotenv

## .env file keys required
### API keys
- <b>DESTINY_API_KEY</b>: Bungie application API key
- <b>DISCORD_API_KEY</b>: Discord application API key
### OAuth
- <b>CLIENT_ID</b>: Bungie application OAuth client_id
- <b>CLIENT_SECRET</b> :Bungie application OAuth client_secret
### Destiny account
- <b>MEMBERSHIP_TYPE</b>: Destiny account's membership type ([reference](https://bungie-net.github.io/multi/schema_BungieMembershipType.html#schema_BungieMembershipType))
- <b>MEMBERSHIP_ID</b>: Destiny account's membership id
- <b>HUNTER_ID</b>: Character id for a hunter belonging to account
- <b>WARLOCK_ID</b>: Character id for a warlock belonging to account
- <b>TITAN_ID</b>: Character id for a titan belonging to account

## Bungie API OAuth setup
<b>For GitHub Pages:</b> The GitHub Pages url will be `[your username].github.io/[your repository]`

- <b>OAuth client type:</b> Confidential
- <b>Redirect URL:</b> <i>`Your GitHub Pages url`</i>
- <b>Scopes:</b> `Read your Destiny 2 information (Vault, Inventory, and Vendors), as well as Destiny 1 Vault and Inventory data.`

## References:
- Bungie.Net API documentation: https://bungie-net.github.io/multi/
- Bungie.Net OAuth documentation: https://github.com/Bungie-net/api/wiki/OAuth-Documentation
- Discord.py documentation: https://discordpy.readthedocs.io/en/stable/#getting-help