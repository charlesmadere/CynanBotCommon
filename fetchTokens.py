import requests


# This file is meant to be run separately from the others in this repository. It retrieves some
# important keys / tokens that are required in order for some Twitch-related functionaly in
# CynanBot and CynanBotDiscord to authenticate with Twitch and run properly.
#
# So before you even run CynanBot itself, you are required to first run this script. Then, you can
# use the output information you've received to build up the information in the secretKeys.py and
# users.py files.

# taken from "Client ID" at https://dev.twitch.tv/console/apps/
TWITCH_CLIENT_ID = None

# taken from "Client Secret" at https://dev.twitch.tv/console/apps/
TWITCH_CLIENT_SECRET = None

# This code is derived from clicking this URL and then authenticating:
# https://id.twitch.tv/oauth2/authorize?response_type=code&client_id=CLIENT_ID_HERE&redirect_uri=http://localhost&scope=chat:read+chat:edit+channel:moderate+whispers:read+whispers:edit+channel_editor+channel:read:redemptions
TWITCH_CODE_SECRET = None

if TWITCH_CLIENT_SECRET is None or TWITCH_CLIENT_SECRET is None or TWITCH_CODE_SECRET is None:
    raise ValueError('TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, and TWITCH_CODE_SECRET must all be set!')

url = f'https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&code={TWITCH_CODE_SECRET}&grant_type=authorization_code&redirect_uri=http://localhost'
rawResponse = requests.post(url)
jsonResponse = rawResponse.json()
accessToken = jsonResponse['access_token']
refreshToken = jsonResponse['refresh_token']
print(f'Twitch accessToken: \"{accessToken}\"')
print(f'Twitch refreshToken: \"{refreshToken}\"')
