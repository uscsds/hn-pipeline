import json
import boto3
import requests
import time
import os

s3 = boto3.client('s3')
bucket = "hn-raw-data-123456"

def lambda_handler(event, context):
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    raw_bucket = os.environ['RAW_BUCKET']
    raw_key = os.environ['RAW_KEY_PREFIX']

    response = requests.get(top_stories_url)
    story_ids = response.json()[:10]  # Fetch top 10 stories 

    stories = []
    for sid in story_ids:
        try:
            data = requests.get(item_url.format(sid)).json()
            stories.append(data)
            time.sleep(0.2)  # Be nice to the API
        except Exception as e:
            print(f"Error with {sid}: {e}")

    filename = f"{int(time.time())}.json"
    s3.put_object(Bucket=raw_bucket, Key=f"{raw_key}_{filename}", Body=json.dumps(stories))
    
    return {"status": "success", "stored": filename}
