"""
Use this if save_session.py didn't work.

Steps:
    1. Install Cookie-Editor extension:
       Chrome → https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm
       Firefox → https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/
    2. Go to https://www.instagram.com (while logged in as aurovoice33)
    3. Open Cookie-Editor → click "Export" → copy the JSON
    4. Create a file named instagram_cookies.json and paste the JSON into it
    5. Run: python import_cookies.py
"""

import os
import json
import instaloader
import requests
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("INSTAGRAM_USERNAME")

if not USERNAME:
    raise ValueError("Missing INSTAGRAM_USERNAME in .env file")

COOKIE_FILE = "safevoice_dataset/scripts/instagram_cookies.json"

if not os.path.exists(COOKIE_FILE):
    raise FileNotFoundError(
        f"'{COOKIE_FILE}' not found.\n"
        "Export cookies from Cookie-Editor extension and save as instagram_cookies.json"
    )

# Load cookies from exported JSON
with open(COOKIE_FILE, "r", encoding="utf-8") as f:
    raw_cookies = json.load(f)

# Build a requests session with these cookies
session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
})

for cookie in raw_cookies:
    session.cookies.set(
        cookie["name"],
        cookie["value"],
        domain=cookie.get("domain", ".instagram.com")
    )

if "sessionid" not in session.cookies:
    raise ValueError(
        "No 'sessionid' cookie found in instagram_cookies.json.\n"
        "Make sure you exported cookies while logged into Instagram."
    )

# Inject session into instaloader
L = instaloader.Instaloader()
L.context._session = session
L.context.username = USERNAME

# Save for future use
session_file = f"session-{USERNAME}"
L.save_session_to_file(session_file)
print(f"Session saved to '{session_file}' — you can now run scrape_instagram.py")