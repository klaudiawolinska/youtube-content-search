CREATE DATABASE IF NOT EXISTS youtube_trends;
USE DATABASE youtube_trends;

CREATE OR REPLACE STAGE youtube_stage;

CREATE OR REPLACE FILE FORMAT json_format
  TYPE = 'JSON'
  STRIP_OUTER_ARRAY = FALSE
  IGNORE_UTF8_ERRORS = TRUE;

CREATE OR REPLACE TABLE videos (
  video_id STRING,
  region STRING,
  title STRING,
  description STRING,
  channel_id STRING,
  channel_title STRING,
  tags ARRAY,
  published_at TIMESTAMP_NTZ,
  views NUMBER,
  likes NUMBER,
  comment_count NUMBER
);

CREATE OR REPLACE TABLE comments (
  video_id STRING,
  comment_id STRING,
  region STRING,
  text STRING,
  published_at TIMESTAMP_NTZ,
  likes NUMBER
);

-- Load your files into stage before you continue!
-- Check that the files have been successfully uploaded to stage
ls @youtube_stage; 

COPY INTO videos
FROM (
  SELECT
    $1:"video_id"::STRING,
    $1:"region"::STRING,
    $1:"title"::STRING,
    $1:"description"::STRING,
    $1:"channel_id"::STRING,
    $1:"channel_title"::STRING,
    $1:"tags"::ARRAY,
    $1:"published_at"::TIMESTAMP_NTZ,
    $1:"views"::NUMBER,
    $1:"likes"::NUMBER,
    $1:"comment_count"::NUMBER
  FROM @youtube_stage/youtube_trending_videos.jsonl (FILE_FORMAT => json_format)
);

COPY INTO comments
FROM (
  SELECT
    $1:"video_id"::STRING,
    $1:"comment_id"::STRING,
    $1:"region"::STRING,
    $1:"text"::STRING,
    $1:"published_at"::TIMESTAMP_NTZ,
    $1:"likes"::NUMBER
  FROM @youtube_stage/youtube_video_comments.jsonl (FILE_FORMAT => json_format)
);
