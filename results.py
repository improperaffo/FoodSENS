import requests
from bs4 import BeautifulSoup
import datetime
import os
# from dotenv import load_dotenv
import json
import http.client
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
# load_dotenv("config.env")
strawPoll_token = os.getenv("STRAW_POLL_TOKEN")
slack_token = os.getenv("SLACK_TOKEN")

# Open menu.txt and store the three lines
with open('menu.txt', 'r') as f:
    lines = f.readlines()

conn = http.client.HTTPSConnection("api.strawpoll.com")

headers = {
    'Content-Type': "application/json",
    'X-API-Key': strawPoll_token
}

# read from url.txt and store the url
with open('url.txt', 'r') as f:
    url = f.readline()
poll_id = url.split("/")[-1]

poll_url = f"/v3/polls/{poll_id}/results"
conn.request("GET", poll_url, headers=headers)

res = conn.getresponse()
data = res.read()

data = json.loads(data)

# Start Slack session
client = WebClient(token=slack_token)

for i, option in enumerate(data['poll_options'][:-1]):
    description = lines[i].replace('\n', '').replace(',', '')
    try:
        response = client.chat_postMessage(
            channel="generale",
            text="Choice: " + description + ", Vote count: " + str(option['vote_count'])
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]
