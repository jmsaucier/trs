import requests
import urllib
import json
import time

def getAccessToken(client_id, client_secret, code, redirect_uri):
    postData = ''
    try:
        postData = "client_id="+ client_id+ "&client_secret="+ client_secret+ "&grant_type=authorization_code"+ "&redirect_uri="+ redirect_uri+ "&code="+ code
    except Exception as e:
        print e
    r = requests.post('https://api.twitch.tv/kraken/oauth2/token', data = postData)
    result = ''
    try:
        result = r.json()
    except Exception as e:
        print e
    token = result['access_token']

    return token

def getUserInformation(client_id, access_token):

    headers = {'Authorization': 'OAuth ' + access_token,
               'Accept': 'application/vnd/twitchtv.v3+json',
               'Client-Id': client_id}

    r = requests.get('https://api.twitch.tv/kraken/user', headers=headers)

    user = r.json()

    return user

def getChannelInfo(client_id, channel):
    headers = {'Accept': 'application/vnd/twitchtv.v3+json',
               'Client-Id': client_id}

    r = requests.get('https://api.twitch.tv/kraken/streams/' + channel, headers=headers)

    result = r.json()

    return result

def getStreamingChannels(client_id, limit = 50):


    headers = {'Accept': 'application/vnd/twitchtv.v3+json',
               'Client-Id': client_id}

    r = requests.get('https://api.twitch.tv/kraken/streams?limit=100&offset=0', headers=headers)

    data = r.json()
    num = len(data["streams"])
    ret = []
    while(num == 100 and data["streams"][0]["viewers"] > limit):
        print data['streams'][len(data['streams']) - 1]['viewers']
        for stream in data["streams"]:
            ret += [(stream["channel"]["name"], stream["game"])]
        r = requests.get(data['_links']['next'], headers=headers)

        data = r.json()

        time.sleep(1)

        num = len(data["streams"])

    for stream in data["streams"]:
            ret += [(stream["channel"]["name"], stream["game"])]

    ret = list(set(ret))
    return ret
