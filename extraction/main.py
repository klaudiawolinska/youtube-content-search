from helpers import (
    init_jsonl, save_jsonl_batch,
    get_most_popular_videos, get_video_comments
)


# ----------------------
# CONFIG
# ----------------------
COUNTRIES = ["PL", "US", "JP", "NG", "BR", "IN", "SA"]
VIDEOS_PER_COUNTRY = 1000   # number of videos per country to be retrieved from API
COMMENTS_PER_VIDEO = 100    # number of comments per video to be retrieved from API

VIDEO_FILE = "output/youtube_trending_videos.jsonl"
COMMENTS_FILE = "output/youtube_video_comments.jsonl"


# ----------------------
# MAIN PIPELINE
# ----------------------
def main():
    # Reset files at start
    init_jsonl(VIDEO_FILE)
    init_jsonl(COMMENTS_FILE)

    for country in COUNTRIES:
        print(f"Fetching trending videos for {country}...")

        for video_page in get_most_popular_videos(country, VIDEOS_PER_COUNTRY):
            save_jsonl_batch(VIDEO_FILE, video_page)

            for v in video_page:
                vid = v["video_id"]
                print(f"Getting comments for video {vid} ({v['title'][:40]}...)")

                try:
                    for comment_page in get_video_comments(vid, v["region"], COMMENTS_PER_VIDEO):
                        save_jsonl_batch(COMMENTS_FILE, comment_page)
                except Exception as e:
                    print(f"Skipped {vid} due to error: {e}")


if __name__ == "__main__":
    main()
