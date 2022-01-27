import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getData(client_id, client_secret):

    # Get the tokens from file to connect to Strava
    with open('Src\strava_tokens_bollie2.json') as json_file:
        strava_tokens = json.load(json_file)
    # If access_token has expired then 
    # use the refresh_token to get the new access_token
    
    # Make Strava auth API call with current refresh token
    response = requests.post(
                        url = 'https://www.strava.com/oauth/token',
                        data = {
                                'client_id': client_id,
                                'client_secret': client_secret,
                                'grant_type': 'refresh_token',
                                'refresh_token': strava_tokens['refresh_token']
                                }
                        )
    # Save the response as a new variable
    new_strava_tokens = response.json()

    # Save the new tokens to file
    with open('Src\strava_tokens_bollie2.json', 'w') as outfile:
        json.dump(new_strava_tokens, outfile)
    
    # Use new Strava tokens from now
    strava_tokens = new_strava_tokens
    
    auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': strava_tokens["refresh_token"],
        'grant_type': "refresh_token",
        'f': 'json'
    }

    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']

    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': 1}

    my_dataset = requests.get(activites_url, headers=header, params=param).json()

    return my_dataset





