from youtube_comment_downloader import YoutubeCommentDownloader
import pandas as pd
import os
from datetime import datetime

# --- Fix path issue (IMPORTANT) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # script location
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "raw", "youtube")
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)

# Ensure directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize downloader
downloader = YoutubeCommentDownloader()

# Video IDs
video_ids = [
    "7aKbdpkMVnU",
]

all_comments = []

for video_id in video_ids:
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Scraping: {url}")
    
    try:
        count = 0
        for comment in downloader.get_comments_from_url(url, sort_by=0):
            all_comments.append({
                "text": comment.get("text", ""),
                "platform": "youtube",
                "video_id": video_id,
                "likes": comment.get("votes", 0),
                "timestamp": comment.get("time", ""),
                "is_reply": comment.get("reply", False),
                "label": "",
                "severity": ""
            })
            count += 1

            if count >= 500:
                break

    except Exception as e:
        print(f"Error scraping {url}: {e}")

# Convert to DataFrame
df = pd.DataFrame(all_comments)

# Clean
df.drop_duplicates(subset=["text"], inplace=True)
df = df[df["text"].str.strip() != ""]

# File name
filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_youtube_comments.csv"
output_path = os.path.join(OUTPUT_DIR, filename)

# Save
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ Saved {len(df)} comments to:\n{output_path}")