import json
import boto3
import os
from datetime import datetime
import re
from textblob import TextBlob
import nltk

# Ensure NLTK points to correct data directory if needed
nltk.data.path.append(os.environ.get("NLTK_DATA", "/tmp"))

s3 = boto3.client('s3')
BUCKET = os.environ['STATE_BUCKET']
STATE_FILE = os.environ['STATE_FILE']

def load_global_seen_ids():
    try:
        response = s3.get_object(Bucket=BUCKET, Key=STATE_FILE)
        content = response['Body'].read().decode('utf-8')
        return set(json.loads(content))
    except s3.exceptions.NoSuchKey:
        return set()

def save_global_seen_ids(seen_ids):
    s3.put_object(Bucket=BUCKET, Key=STATE_FILE, Body=json.dumps(list(seen_ids)))

def clean_story(story):
    if story.get('deleted') or story.get('dead'):
        return None
    if 'title' not in story:
        return None
    title = story['title'].strip()
    text = story.get('text', '').strip() if story.get('text') else None
    if text:
        text = re.sub(r'<[^>]+>', '', text).lower()
    title = title.lower()
    blob = TextBlob(f'{title} {text}')
    sentiment = blob.sentiment.polarity
    return {
        'id': story.get('id'),
        'title': title or '',
        'score': story.get('score') or 0,
        'time': story.get('time'),
        'text': text or '',
        'sentiment': round(sentiment, 2),
        'kidsSize': len(story.get('kids', [])),
        'url': story.get('url', [])
    }

def load_json_from_s3(key):
    try:
        response = s3.get_object(Bucket=BUCKET, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except s3.exceptions.NoSuchKey:
        print(f"No such file {key}, initializing empty.")
        return None
    except Exception as e:
        print(f"Failed to load {key}: {e}")
        return None

def lambda_handler(event, context):
    raw_bucket = os.environ['RAW_BUCKET']
    clean_bucket = os.environ['CLEAN_BUCKET']
    clean_key_prefix = os.environ['CLEAN_KEY_PREFIX']
    raw_key_prefix = os.environ['RAW_KEY_PREFIX']
    unique_stories_file = f'{clean_key_prefix}_all.json'
    # Load seen ids at the beginning
    seen_ids = load_global_seen_ids()

    # Load global stories list
    unique_stories = load_json_from_s3(unique_stories_file) or []

    # Read new raw HN dump file (use event to get the key)
    if 'Records' in event:
        record = event['Records'][0]
        key = record['s3']['object']['key']
    else:
        print("🔹 Triggered by non-S3 event (e.g., CloudWatch schedule)")
        return {
            'statusCode': 200,
            'body': '🔹 Triggered by non-S3 event (e.g., CloudWatch schedule)'}
    postfix = re.sub(raw_key_prefix + "_", "", key)
    timestamp = re.sub(".json", "", postfix)
    raw_data = s3.get_object(Bucket=raw_bucket, Key=key)
    stories = json.loads(raw_data['Body'].read())

    new_stories = []
    for story in stories:
        if story['id'] not in seen_ids:
            cleaned_story = clean_story(story)
            new_stories.append(cleaned_story)
            unique_stories.append(cleaned_story)
            seen_ids.add(story['id'])


    # Save updated seen_ids back to state/
    save_global_seen_ids(seen_ids)

    # (Save new_stories to cleaned/ location)
    s3.put_object(Bucket=clean_bucket, Key=f'{clean_key_prefix}_{timestamp}.json', Body=json.dumps(new_stories))

    # Save global unique stories
    s3.put_object(Bucket=clean_bucket, Key=unique_stories_file, Body=json.dumps(unique_stories))

    return {
        'statusCode': 200,
        'body': f'Processed {len(new_stories)} new stories and updated global stories list.'
    }
