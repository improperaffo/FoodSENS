import os
# from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
# load_dotenv("config.env")
slack_token = os.getenv("SLACK_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Start Slack session
client = WebClient(token=slack_token)

# Read URL from url.txt
with open('url.txt', 'r') as f:
    url = f.readline()

try:
    response = client.chat_postMessage(
        channel=CHANNEL_ID,
        text=":warning: Two hours left for chosing the food for next Wednesday! :warning: \n Link: " + url
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]
