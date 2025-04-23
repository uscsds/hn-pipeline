import json
import boto3
import os
from datetime import datetime
import re

def clean_story(story):
    # Drop stories marked as deleted or dead
    if story.get('deleted') or story.get('dead'):
        return None

    # Must have a title
    if 'title' not in story:
        return None

    title = story['title'].strip()
    text = story.get('text', '').strip() if story.get('text') else None

    # Normalize fields: lowercase, remove HTML tags from text
    if text:
        text = re.sub(r'<[^>]+>', '', text).lower()
    title = title.lower()

    return {
        'id': story.get('id'),
        'title': title,
        'score': story.get('score'),
        'time': story.get('time'),
        'text': text,
        'kids': story.get('kids', [])
    }

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    raw_bucket = os.environ['RAW_BUCKET']
    clean_bucket = os.environ['CLEAN_BUCKET']
    raw_key = os.environ['RAW_KEY']  # e.g., raw/hn_dump.json
    clean_key = os.environ['CLEAN_KEY']  # e.g., cleaned/hn_cleaned.json

    obj = s3.get_object(Bucket=raw_bucket, Key=raw_key)
    raw_data = json.loads(obj['Body'].read())

    cleaned = [clean_story(item) for item in raw_data if clean_story(item)]

    s3.put_object(
        Bucket=clean_bucket,
        Key=clean_key,
        Body=json.dumps(cleaned)
    )