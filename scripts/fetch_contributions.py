"""Fetch the public contribution calendar for a GitHub user (no token needed)
and write data/contributions.json with raw days plus derived stats."""
import json
import os
import re
import sys
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USER", "manyashri1901")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days(username):
    url = f"https://github.com/users/{username}/contributions"
    r = requests.get(url, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Map cell id -> count from the tooltips ("3 contributions on ...").
    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d+)\s+contribution", tip.get_text())
        if m:
            counts[tip.get("for")] = 0 if m.group(1) == "No" else int(m.group(1))

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        days.append(
            {
                "date": d,
                "count": counts.get(td.get("id"), 0),
                "level": int(td.get("data-level", 0)),
            }
        )
    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    today = date.today().isoformat()
    by_date = {d["date"]: d["count"] for d in days}
    total = sum(d["count"] for d in days)

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    # Current streak: walk back from today (or yesterday if today is empty).
    cur = 0
    cursor = date.today()
    if by_date.get(cursor.isoformat(), 0) == 0:
        cursor -= timedelta(days=1)
    while by_date.get(cursor.isoformat(), 0) > 0:
        cur += 1
        cursor -= timedelta(days=1)

    best = max(days, key=lambda d: d["count"]) if days else {"date": today, "count": 0}
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]

    return {
        "total": total,
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": months,
    }


def main():
    days = fetch_days(USERNAME)
    if not days:
        sys.exit("No contribution cells found - GitHub markup may have changed.")
    data = {"username": USERNAME, "days": days, "stats": derive_stats(days)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, indent=1)
    s = data["stats"]
    print(f"{len(days)} days, {s['total']} contributions, "
          f"streak {s['current_streak']} (longest {s['longest_streak']})")


if __name__ == "__main__":
    main()
