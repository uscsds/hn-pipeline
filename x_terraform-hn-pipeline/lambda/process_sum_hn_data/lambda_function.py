import json
import boto3
import os

s3 = boto3.client('s3')

BUCKET = os.environ.get('BUCKET_NAME')
CLEANED_PREFIX = 'cleaned/'
SUMMARY_STATE_FILE = 'state/summary_state.json'
GLOBAL_SEEN_FILE = 'state/global_seen_ids.json'
UNIQUE_STORIES_FILE = 'state/unique_stories.json'

def lambda_handler(event, context):
    # Load or initialize summary state
    summary_state = load_json_from_s3(SUMMARY_STATE_FILE) or {"last_processed": None, "processed_files": []}
    global_seen_ids = load_json_from_s3(GLOBAL_SEEN_FILE) or []
    unique_stories = load_json_from_s3(UNIQUE_STORIES_FILE) or []

    # List all cleaned JSON files
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix=CLEANED_PREFIX)
    files = sorted([obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.json')])

    new_files = [f for f in files if f not in summary_state['processed_files']]
    if not new_files:
        print("No new files to process.")
        return {
            'statusCode': 200,
            'body': json.dumps('No new data to process')
        }

    for file_key in new_files:
        print(f"Processing {file_key}")
        data = load_json_from_s3(file_key)
        if not data:
            continue

        for story in data:
            story_id = story.get('id')
            if story_id and story_id not in global_seen_ids:
                # Build the unique story entry
                unique_entry = {
                    'id': story.get('id'),
                    'title': story.get('title', ''),
                    'score': story.get('score', 0),
                    'text_length': len(story.get('text', '')),
                    'kids_size': len(story.get('kids', [])) if 'kids' in story else 0,
                    'url': story.get('url', ''),
                    'sentiment': story.get('sentiment', 0)
                }
                unique_stories.append(unique_entry)
                global_seen_ids.append(story_id)

        # Update state
        summary_state['processed_files'].append(file_key)
        summary_state['last_processed'] = file_key

    # Save updated files
    save_json_to_s3(summary_state, SUMMARY_STATE_FILE)
    save_json_to_s3(global_seen_ids, GLOBAL_SEEN_FILE)
    save_json_to_s3(unique_stories, UNIQUE_STORIES_FILE)

    return {
        'statusCode': 200,
        'body': json.dumps(f"Processed {len(new_files)} new files.")
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

def save_json_to_s3(data, key):
    try:
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
    except Exception as e:
        print(f"Failed to save {key}: {e}")
