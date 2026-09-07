import os
import csv
from datetime import datetime, timezone
import requests

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
OPTIONS = ["Quran", "Hedis", "Seher/Axşam zikrleri", "Kitab", "Jim", "Su"]

url = f"https://api.telegram.org/bot{TOKEN}/sendPoll"
payload = {
    "chat_id": CHAT_ID,
    "question": "Verdişlər",
    "options": OPTIONS,
    "is_anonymous": False,
    "allows_multiple_answers": True,
}

response = requests.post(url, json=payload)
response.raise_for_status()
result = response.json()["result"]
poll_id = result["poll"]["id"]
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

log_path = "polls_log.csv"
file_exists = os.path.exists(log_path)
with open(log_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["date", "poll_id"])
    writer.writerow([today, poll_id])

print(f"Poll sent: {poll_id} on {today}")
