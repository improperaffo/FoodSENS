import requests
from bs4 import BeautifulSoup
import datetime
import os
#from dotenv import load_dotenv
import json
import http.client
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
#load_dotenv("config.env")
strawPoll_token = os.getenv("STRAW_POLL_TOKEN")
slack_token = os.getenv("SLACK_TOKEN")

# Read channel ID from channel.txt
with open('channel.txt', 'r') as f:
    CHANNEL_ID = f.read().strip()

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

# Load list of vote options from lines
vote_options = [line.replace('\n', '') for line in lines]

# Go though all poll_participants, store their name and poll_votes
participants = []
for participant in data['poll_participants']:
    name = participant['name']
    votes = participant['poll_votes']
    participants.append((name, votes))

# Write the results to result.txt, for each vote_option, count the votes and print the names of who voted it. Every line should contain the vote_option, the number of votes and the names of the voters.
# participant.votes are bitmaps, where the i-th bit is set if the participant voted for the i-th option
with open('results.txt', 'w') as f:
    for i, option in enumerate(vote_options):
        votes = 0
        voters = []
        for j, participant in enumerate(participants):
            if participant[1][i] == 1:
                votes += 1
                voters.append(participant[0])
        f.write(f"Option: {option}, Voters: {', '.join(voters)}\n")

# Start Slack session
client = WebClient(token=slack_token)

try:
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text="This week lunch choices are :pizza: :burger: :poultry_leg: "
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]

for i, option in enumerate(data['poll_options']):
    description = lines[i].replace('\n', '').replace(',', '')
    try:
        response = client.chat_postMessage(
            channel=CHANNEL_ID,
            text="Choice: " + description + ", *Vote count:* " + str(option['vote_count'])
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]

total_participants = data['participant_count']
try:
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text="Total participants: " + str(total_participants)
    )
except SlackApiError as e:  # You will get a SlackApiError if "ok" is False
    assert e.response["error"]

try:
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text="Detailed results: github.com/improperaffo/FoodSENS/blob/main/results.txt"
    )
except SlackApiError as e:  # You will get a SlackApiError if "ok" is False
    assert e.response["error"]
