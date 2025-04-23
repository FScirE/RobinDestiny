# Robin D. Estiny
### A discord.py bot connected to the Bungie.Net API

## Features:
- Finding players by Bungie name
- Getting specific player information about their characters and platforms
- Seeing weekly grandmaster nightfall information
- Getting weekly adept nightfall weapon
- Browsing all weekly bright dust items from Eververse

## .env file keys required
### API keys
- DESTINY_API_KEY
    - <b>Bungie application API key</b>
- DISCORD_API_KEY
    - <b>Discord application API key</b>
### OAuth
- CLIENT_ID
    - <b>Bungie application OAuth client_id</b>
- CLIENT_SECRET
    - <b>Bungie application OAuth client_secret</b>
### Destiny account
- MEMBERSHIP_TYPE
    - <b>Destiny account's membership type ([reference](https://bungie-net.github.io/multi/schema_BungieMembershipType.html#schema_BungieMembershipType))</b>
- MEMBERSHIP_ID
    - <b>Destiny account's membership id</b>
- HUNTER_ID
    - <b>Character id for a hunter</b>
- WARLOCK_ID
    - <b>Character id for a warlock</b>
- TITAN_ID
    - <b>Character id for a titan</b>

## References:
- Bungie.Net API documentation: https://bungie-net.github.io/multi/
- Bungie.Net OAuth documentation: https://github.com/Bungie-net/api/wiki/OAuth-Documentation
- Discord.py documentation: https://discordpy.readthedocs.io/en/stable/#getting-help