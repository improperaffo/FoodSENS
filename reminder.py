import os
#from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import http.client

# Load environment variables
#load_dotenv("config.env")
strawPoll_token = os.getenv("STRAW_POLL_TOKEN")
slack_token = os.getenv("SLACK_TOKEN")

# Read channel ID from channel.txt
with open('channel.txt', 'r') as f:
    CHANNEL_ID = f.read().strip()

# Read URL from url.txt
with open('url.txt', 'r') as f:
    url = f.readline()

conn = http.client.HTTPSConnection("api.strawpoll.com")

headers = {
    'Content-Type': "application/json",
    'X-API-Key': strawPoll_token
}

print(headers)

poll_id = url.split("/")[-1]

poll_url = f"/v3/polls/{poll_id}/results"
conn.request("GET", poll_url, headers=headers)

# Remove https:// from the URL
url = url[8:]

res = conn.getresponse()
data = res.read()

data = json.loads(data)

# Go though all poll_participants, store their name and poll_votes
participants = []
for participant in data['poll_participants']:
    name = participant['name']
    participants.append(name)

# Start Slack session
client = WebClient(token=slack_token)

try:    
    # Send the reminder message to the Slack channel
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text=":warning: Two hours left for choosing the food for next Wednesday! :warning: \n\nParticipants who have already voted: " + ", ".join(participants) + "\n\nLink: " + url
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]
