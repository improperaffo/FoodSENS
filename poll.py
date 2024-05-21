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

# Calculate the date of the next Wednesday
today = datetime.date.today()
days_ahead = (4 - today.weekday()) % 7 # Choose 2 for next Wednesday
next_wednesday = today + datetime.timedelta(days=days_ahead)

# Format the date in the required format
date_str = next_wednesday.strftime("%Y-%m-%d")

# Print date
print("Looking for menu of "+date_str)

# Open the JSON file and load the data
with open('template.json', 'r') as f:
    data = json.load(f)

# List of new values
new_values = []

# Read menu.txt and store every line in menu_items
with open('menu.txt', 'r') as f:
    menu_items = f.readlines()

for item in menu_items:
    b_tag = item.find('b')
    if b_tag is not None:
        descr = b_tag.contents[0]
        if descr is not None:
            new_values.append(descr.strip().replace('\n', ' '))

# For each poll option, change the value
for i, option in enumerate(data['poll_options'][:-2]):
    option['value'] = new_values[i]

# Calculate the date of the next Monday
today = datetime.date.today()
days_ahead = (0 - today.weekday()) % 7
next_monday = today + datetime.timedelta(days=days_ahead)

# Convert the date to a datetime at the start of the day
next_monday = datetime.datetime.combine(next_monday, datetime.time())

# Set the time to 12:00
next_monday_at_12 = next_monday.replace(hour=12, minute=0, second=0)

# Convert to a Unix timestamp
deadline = int(next_monday_at_12.timestamp())

# Update the deadline in the data
data['poll_config']['deadline_at'] = deadline
data['poll_meta']['description'] = f"For more information: {url}"

conn = http.client.HTTPSConnection("api.strawpoll.com")

# Create poll
payload = json.dumps(data)

headers = {
    'Content-Type': "application/json",
    'X-API-Key': strawPoll_token
}

conn.request("POST", "/v3/polls", payload, headers)

res = conn.getresponse()
data = res.read()

# Save response
loaded_data = json.loads(data)

# Get URL from response
url = loaded_data["embed_url"]
print(url)

# Write the URL to a file
with open("url.txt", "w") as file:
    file.write(url)

# Start Slack session
client = WebClient(token=slack_token)

try:
    response = client.chat_postMessage(
        channel="generale",
        text="Make your food choice for the next group meeting: " + url
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]
