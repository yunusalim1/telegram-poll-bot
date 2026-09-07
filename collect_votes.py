import os
import csv
import json
from datetime import datetime, timezone
import requests

TOKEN = os.environ["BOT_TOKEN"]
OPTIONS = ["Quran", "Hedis", "Seher/Axşam zikrleri", "Kitab", "Jim", "Su"]

OFFSET_FILE = "last_update_id.txt"
POLLS_LOG = "polls_log.csv"
VOTES_FILE = "votes.csv"

offset = 0
if os.path.exists(OFFSET_FILE):
    content = open(OFFSET_FILE).read().strip()
    if content:
        offset = int(content) + 1

poll_date = {}
if os.path.exists(POLLS_LOG):
    with open(POLLS_LOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            poll_date[row["poll_id"]] = row["date"]

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
params = {
    "offset": offset,
    "timeout": 0,
    "allowed_updates": json.dumps(["poll_answer"]),
}
resp = requests.get(url, params=params)
resp.raise_for_status()
data = resp.json()

new_rows = []
max_update_id = offset - 1

for update in data.get("result", []):
    max_update_id = max(max_update_id, update["update_id"])
    pa = update.get("poll_answer")
    if not pa:
        continue
    poll_id = pa["poll_id"]
    user = pa.get("user", {})
    user_id = user.get("id")
    first_name = user.get("first_name", "")
    option_ids = pa.get("option_ids", [])
    options_text = ";".join(OPTIONS[i] for i in option_ids if i < len(OPTIONS))
    date = poll_date.get(poll_id, datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    new_rows.append([update["update_id"], date, poll_id, user_id, first_name, options_text])

if new_rows:
    file_exists = os.path.exists(VOTES_FILE)
    with open(VOTES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["update_id", "date", "poll_id", "user_id", "first_name", "options"])
        writer.writerows(new_rows)

with open(OFFSET_FILE, "w") as f:
    f.write(str(max_update_id))

print(f"Collected {len(new_rows)} new vote events. New offset: {max_update_id}")
