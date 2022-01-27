# IMPORTANT - This code can only run once! 
import requests
import json
# Make Strava auth API call with your 
# client_code, client_secret and code
response = requests.post(
                    url = 'https://www.strava.com/oauth/token',
                    data = {
                            'client_id':75133,
                            'client_secret': 'b32174d53ebd5bce6f78a2c398efa45654f4e556',
                            'code': 'b1658757bd4703df6c65db70052b7aea507ecfd8',
                            'grant_type': 'authorization_code'
                            }
                )
#Save json response as a variable
strava_tokens = response.json()
# Save tokens to file
with open('strava_tokens_bollie2.json', 'w') as outfile:
    json.dump(strava_tokens, outfile)


# Id and secret - Bollie
# 75133
# b32174d53ebd5bce6f78a2c398efa45654f4e556
# 98d12ad72d9f276577e5fc6f0610f61a249a1fe4
# https://www.strava.com/oauth/token?client_id=75133&client_secret=b32174d53ebd5bce6f78a2c398efa45654f4e556&code=98d12ad72d9f276577e5fc6f0610f61a249a1fe4&grant_type=authorization_code
# http://localhost/exchange_token?state=&code=b1658757bd4703df6c65db70052b7aea507ecfd8&scope=read,activity:read_all,profile:read_all