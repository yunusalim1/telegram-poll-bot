import os
from datetime import datetime, timezone
import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
VOTES_FILE = "votes.csv"

AY_ADLARI = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "İyun",
             "İyul", "Avqust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]

now = datetime.now(timezone.utc)
year = now.year
month = now.month - 1
if month == 0:
    month = 12
    year -= 1
month_str = f"{year}-{month:02d}"

if not os.path.exists(VOTES_FILE):
    print("votes.csv hələ yoxdur, keçilir.")
    raise SystemExit(0)

df = pd.read_csv(VOTES_FILE, dtype=str)
df = df[df["date"].str.startswith(month_str)]

if df.empty:
    print(f"{month_str} üçün heç bir cavab tapılmadı.")
    raise SystemExit(0)

df["update_id"] = df["update_id"].astype(int)
df = df.sort_values("update_id").drop_duplicates(subset=["poll_id", "user_id"], keep="last")

rows = []
for _, r in df.iterrows():
    opts = r["options"]
    if pd.isna(opts) or opts == "":
        continue
    for opt in opts.split(";"):
        rows.append({"user": r["first_name"], "option": opt})

exp = pd.DataFrame(rows)
if exp.empty:
    print(f"{month_str} üçün işarələnmiş verdiş yoxdur.")
    raise SystemExit(0)

pivot = exp.pivot_table(index="user", columns="option", values="option", aggfunc="count", fill_value=0)

fig, ax = plt.subplots(figsize=(10, 6))
pivot.plot(kind="bar", ax=ax)
ax.set_title(f"{AY_ADLARI[month - 1]} {year} — Verdişlər statistikası")
ax.set_ylabel("Gün sayı")
ax.set_xlabel("")
plt.xticks(rotation=20)
plt.legend(title="Verdiş", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

chart_path = "monthly_chart.png"
plt.savefig(chart_path, dpi=150)

totals = pivot.sum(axis=1).sort_values(ascending=False)
lines = [f"📊 {AY_ADLARI[month - 1]} {year} statistikası:\n"]
for user, total in totals.items():
    lines.append(f"{user}: {int(total)} gün")
caption = "\n".join(lines)[:1024]

url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
with open(chart_path, "rb") as photo:
    resp = requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})
resp.raise_for_status()
print("Aylıq statistika göndərildi.")
