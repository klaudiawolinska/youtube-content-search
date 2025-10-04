USE DATABASE youtube_trends;
USE SCHEMA public;

-- ----------------------------------------------------------------------------------
-- 1. Comments Search Service
-- ----------------------------------------------------------------------------------
CREATE OR REPLACE CORTEX SEARCH SERVICE youtube_trends.public.youtube_comments_svc
ON text_translated
ATTRIBUTES region
WAREHOUSE = compute_wh
TARGET_LAG = '1 hour'
AS
    SELECT
        c.video_id,
        v.title,
        c.region,
        c.text,
        AI_TRANSLATE(text, '', 'en') AS text_translated,
        c.published_at,
        c.likes
    FROM
    youtube_trends.public.comments c
    LEFT JOIN youtube_trends.public.videos v 
    ON c.video_id = v.video_id;

-- ----------------------------------------------------------------------------------
-- 2. Videos Search Service
-- ----------------------------------------------------------------------------------
CREATE OR REPLACE CORTEX SEARCH SERVICE youtube_trends.public.youtube_videos_svc
ON desc_translated
ATTRIBUTES region
WAREHOUSE = compute_wh
TARGET_LAG = '1 hour'
AS
    SELECT
        region,
        title,
        description,
        AI_TRANSLATE(description, '', 'en') AS desc_translated,
        channel_title,
        published_at,
        views,
        likes,
        comment_count
    FROM
    youtube_trends.public.videos;
