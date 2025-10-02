import os
import json
import time
from googleapiclient.discovery import build


# ----------------------
# CONFIG
# ----------------------
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("Missing YOUTUBE_API_KEY environment variable")

YOUTUBE = build("youtube", "v3", developerKey=API_KEY)


# ----------------------
# JSON HELPERS
# ----------------------
def init_jsonl(filename):
    """Create/overwrite a JSONL file at the start of a run."""

    with open(filename, "w", encoding="utf-8") as f:
        f.write("")  # clear the file

def save_jsonl_batch(filename, records):
    """Append a batch of records to an NDJSON file."""

    with open(filename, "a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ----------------------
# YOUTUBE HELPERS
# ----------------------
def get_most_popular_videos(region, max_videos):
    """Fetch most popular videos for a given country with pagination."""

    fetched = 0
    
    request = YOUTUBE.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region,
        maxResults=50
    )

    while request and fetched < max_videos:
        response = request.execute()
        page_videos = []

        for item in response.get("items", []):
            page_videos.append({
                "video_id": item["id"],
                "region": region,
                "title": item["snippet"].get("title"),
                "description": item["snippet"].get("description"),
                "channel_id": item["snippet"].get("channelId"),
                "channel_title": item["snippet"].get("channelTitle"),
                "tags": item["snippet"].get("tags"),
                "published_at": item["snippet"].get("publishedAt"),
                "views": int(item["statistics"].get("viewCount", 0)),
                "likes": int(item["statistics"].get("likeCount", 0)),
                "comment_count": int(item["statistics"].get("commentCount", 0))
            })

            fetched += 1
            if fetched >= max_videos:
                break
        
        yield page_videos  # return max 50 videos at once

        request = YOUTUBE.videos().list_next(request, response)
        time.sleep(0.2)  # avoid hitting rate limits


def get_video_comments(video_id, region, max_comments):
    """Fetch top-level comments for a given video with pagination."""

    request = YOUTUBE.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    fetched = 0

    while request and fetched < max_comments:
        response = request.execute()

        page_comments = []

        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]
            snippet = top_comment["snippet"]

            page_comments.append({
                "video_id": video_id,
                "comment_id": top_comment["id"],
                "region": region,
                "text": snippet.get("textDisplay"),
                "published_at": snippet.get("publishedAt"),
                "likes": int(snippet.get("likeCount", 0))
            })

            fetched += 1
            if fetched >= max_comments:
                break
        
        yield page_comments  # return max 100 comments at once

        request = YOUTUBE.commentThreads().list_next(request, response)
        time.sleep(0.2)  # avoid hitting rate limits
