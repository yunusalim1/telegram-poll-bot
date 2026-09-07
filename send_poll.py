import os
import requests

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{TOKEN}/sendPoll"

payload = {
    "chat_id": CHAT_ID,
    "question": "Verdişlər",
    "options": ["Quran", "Hedis", "Seher/Axşam zikrleri", "Kitab", "Jim", "Su"],
    "is_anonymous": False,
    "allows_multiple_answers": True,
}

response = requests.post(url, json=payload)
response.raise_for_status()
print(response.json())
