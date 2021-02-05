# Get elon musks most recent tweet, with a maximum of 1.1 seconds delay


import requests
import os
import json
import time

with open("twitter_secrets.txt", "r") as ts:
    bearer_token = ts.read().split("\n")[-2]
def auth():
    return (bearer_token)

def create_lookup_url():
    query = "from:elonmusk"
    tweet_fields = "tweet.fields=author_id"
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=elonmusk&count=1&tweet_mode=extended".format(
        query, tweet_fields
    )
    return url



def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()


def get_user_id():
    bearer_token = auth()
    url = create_lookup_url()
    headers = create_headers(bearer_token)
    json_response = connect_to_endpoint(url, headers)
    tweet = json_response[0]
    return [tweet["full_text"], tweet["created_at"]]
    # return (json.dumps(json_response, indent=4, sort_keys=True))




if __name__ == "__main__":
    old_tweet = [""]
    while True:
        try:
            tweet = get_user_id()
            if tweet[0] != old_tweet[0]:
                old_tweet = tweet
                print("New tweet")
                print("Time: ", old_tweet[1])
                print("Text: ", old_tweet[0])
        except:
            pass
        time.sleep(1.1)
