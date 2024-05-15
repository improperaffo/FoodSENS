import os
#from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables
#load_dotenv("config.env")
slack_token = os.getenv("SLACK_TOKEN")

# Start Slack session
client = WebClient(token=slack_token)

try:
    response = client.chat_postMessage(
        channel="generale",
        text="One hour left for chosing the food"
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]
