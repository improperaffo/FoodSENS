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

# Calculate the date of the next Wednesday
today = datetime.date.today()
days_ahead = (2 - today.weekday()) % 7
next_wednesday = today + datetime.timedelta(days=days_ahead)

# Format the date in the required format
date_str = next_wednesday.strftime("%Y-%m-%d")

# Print date
print("Looking for menu of "+date_str)

# Make a request to the website with the updated date
url = f"https://www.epfl.ch/campus/restaurants-shops-hotels/self-service-2/foodlab-alpine/?date={date_str}"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
html_content = r.content

# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Find the first three 'menu-content' elements
menu_items = soup.find_all(class_='menu-content', limit=3)

# Open the JSON file and load the data
with open('template.json', 'r') as f:
    data = json.load(f)

# List of new values
new_values = []

# For each 'menu-content' element, find the <b> tag, get the next sibling and write its text to the file
with open('/home/sens/FoodLab_menu/options.txt', 'w') as file:
    for item in menu_items:
        b_tag = item.find('b')
        if b_tag is not None:
            descr = b_tag.contents[0]
            if descr is not None:
                new_values.append(descr.strip().replace('\n', ' '))



# For each poll option, change the value
for i, option in enumerate(data['poll_options'][:-1]):
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
