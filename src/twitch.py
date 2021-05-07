import requests
import json
import urllib
import os
import settings

# Uses the Twitch API to fetch profile pictures of racers
def fetchProfiles(users):
    for user in users:
        path = os.path.join(settings.baseDir,"profiles/"+user+".png")
        if not os.path.isfile(path):
            url = "https://api.twitch.tv/helix/users?login="+user
            headers = {"Client-ID":client_id, "Authorization":f'Bearer {token}'}
            response = requests.get(url, headers=headers)
            if response.status_code in range(200,300):
                responseData = json.loads(response.content.decode("UTF-8"))['data']
                if len(responseData)==0:
                    print("[API] Twitch user "+user+" does not exist. Using default image.")
                    #playerLookup[user].validTwitchAccount = False
                else:
                    data = responseData[0]
                    profileLocation = data['profile_image_url']
                    urllib.request.urlretrieve(profileLocation, "."+"/profiles/"+user+".png")
                    print("[API] Fetched profile of Twitch user "+user+".")
            else:
                print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
    return

def getTwitchId(user):
    url = "https://api.twitch.tv/helix/users?login="+user
    headers = {"Client-ID":client_id, "Authorization":f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code in range(200,300):
        responseData = json.loads(response.content.decode("UTF-8"))['data']
        if len(responseData)==0:
            print("[API] Twitch user "+user+" does not exist.")
            return None
        else:
            id = responseData[0]['id']
            print("[API] Fetched id of Twitch user "+user+": "+id+".")
            return id
    else:
        print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
        return None

def updateSet(data):
    updated = {}
    for user in data:
        id = data[user]
        url = "https://api.twitch.tv/helix/users?id="+id
        headers = {"Client-ID":client_id, "Authorization":f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code in range(200,300):
            responseData = json.loads(response.content.decode("UTF-8"))['data']
            if len(responseData)==0:
                print("[API] Twitch id "+id+" does not exist.")
            else:
                newUsername = responseData[0]['login']
                updated[newUsername] = id
                if user != newUsername:
                    print("[API] Updated username of Twitch id "+id+": "+user+" -> "+newUsername)
        else:
            print('[API] Twitch API Request Failed: ' + response.content.decode("UTF-8"))
            return None
    return updated

def check_token():
    print("Validating Twitch API token...")
    r = requests.get('https://id.twitch.tv/oauth2/validate', headers={'Client-ID': client_id, 'Authorization': f'Bearer {token}'})
    #print(r.json())
    if r.status_code != 200:
        print("Token invalid. Requesting a new one...")
        new_token()
    elif r.json()['expires_in'] < 604800:
        print("Old token. Requesting a new one...")
        #token expires in < 1 week
        new_token()
    else:
        print("Token is valid.")

def new_token():
    r2 = requests.post('https://id.twitch.tv/oauth2/token', data={'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials'})
    #print(r2.json())
    global token
    token = r2.json()['access_token']
    with open(os.path.join(settings.baseDir,'settings.json'), 'r+') as f:
        j = json.load(f)
        j['twitch-api-token'] = token
        f.seek(0)
        json.dump(j, f, indent=4)
        f.truncate()
    print("New token received.")

token = settings.twitch_token
client_id = settings.twitch_clientid
client_secret = settings.twitch_secret

check_token()
