"""
Run this ONCE to import your Instagram session from the browser.
After this, scrape_instagram.py will use the saved session file.

Requirements:
    pip install instaloader python-dotenv

Steps:
    1. Log into https://www.instagram.com in Chrome/Firefox manually
    2. Run: python save_session.py
    3. Then run: python scrape_instagram.py
"""

import os
import instaloader
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("INSTAGRAM_USERNAME")

if not USERNAME:
    raise ValueError("Missing INSTAGRAM_USERNAME in .env file")

L = instaloader.Instaloader()

# Import session cookies directly from your browser (no password used)
# This avoids all checkpoint / bot-detection issues
try:
    # Try Chrome first
    L.load_session_from_file(USERNAME)
    print(f"Session already exists for {USERNAME}. You're good to go!")

except FileNotFoundError:
    print("No saved session found. Importing from browser cookies...\n")

    try:
        # Import from Firefox
        import sqlite3, glob, http.cookiejar

        # Locate Firefox cookie DB
        firefox_profiles = glob.glob(
            os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\*.default-release\\cookies.sqlite")
        )

        if not firefox_profiles:
            firefox_profiles = glob.glob(
                os.path.expanduser("~/.mozilla/firefox/*.default-release/cookies.sqlite")
            )

        if firefox_profiles:
            import tempfile, shutil
            # Copy DB (Firefox locks it while open)
            tmp = tempfile.mktemp(suffix=".sqlite")
            shutil.copy2(firefox_profiles[0], tmp)

            conn = sqlite3.connect(tmp)
            cur = conn.cursor()
            cur.execute(
                "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
            )
            cookies = {row[0]: row[1] for row in cur.fetchall()}
            conn.close()
            os.remove(tmp)

            if "sessionid" not in cookies:
                raise ValueError("No Instagram session found in Firefox. Make sure you're logged in.")

            # Inject cookies into instaloader context
            import requests
            session = requests.Session()
            session.cookies.update(cookies)
            session.headers.update({"User-Agent": "Mozilla/5.0"})

            L.context._session = session
            L.context.username = USERNAME
            L.save_session_to_file(f"session-{USERNAME}")
            print(f"Session saved from Firefox → 'session-{USERNAME}'")

        else:
            raise FileNotFoundError("Firefox profile not found.")

    except Exception as e:
        print(f"Browser import failed: {e}")
        print("\n── Manual cookie method ──────────────────────────────────────")
        print("1. Install the 'Cookie-Editor' extension in Chrome or Firefox")
        print("   Chrome: https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm")
        print("   Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/")
        print("2. Go to https://www.instagram.com (while logged in)")
        print("3. Open Cookie-Editor → click Export → copy the JSON")
        print("4. Paste it into a file named: instagram_cookies.json")
        print("5. Run: python import_cookies.py")