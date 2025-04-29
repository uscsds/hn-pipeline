import json
import os
import glob
from datetime import datetime
import re
from textblob import TextBlob
#import nltk
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

STATE_FILE = "state/global_seen_ids.json"

def load_raw_filepaths(data_folder):
    all_files = glob.glob(os.path.join(data_folder, "*raw_*.json"))
    return all_files

def load_json_file(data_path):
    print('Loading json file: ' + data_path)
    try:
        with open(data_path, "r") as f:
            return json.load(f)
    except:
        return []

def load_raw_files(data_folder):
    all_files = glob.glob(os.path.join(data_folder, "*raw_*.json"))
    for file in all_files:
        with open(file, "r") as f:
            yield json.load(f)

def save_json_file(output_path, data):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

def load_global_seen_ids():
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.loads(f))
    except:
        return set()

def save_global_seen_ids(seen_ids):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen_ids), f, indent=2)

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

def clean_data():
    raw_bucket = "raw/"
    clean_bucket = "cleaned/"
    clean_key_prefix = "cleaned/hn_top_cleaned"
    raw_key_prefix ="raw/hn_top_raw"
    raw_prefix = "hn_top_raw_"
    unique_stories_file = f'{clean_key_prefix}_all.json'
    # Load seen ids at the beginning
    seen_ids = load_global_seen_ids()

    # Load global stories list
    unique_stories = load_json_file(unique_stories_file) or []

    count = 0
    # Read raw HN dump file and process cleanning
    for filepath in load_raw_filepaths(raw_bucket):
        key = re.sub(raw_key_prefix + "_", "", filepath)
        timestamp = re.sub(".json", "", key)
        stories = load_json_file(filepath)

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
        save_json_file(f'{clean_key_prefix}_{timestamp}.json', new_stories)
        
        # Save global unique stories
        save_json_file(unique_stories_file, unique_stories)

        print(f'Processed {len(new_stories)} new stories and updated global stories list.')
        count += len(new_stories)

    return {
        'statusCode': 200,
        'body': f'Processed {count} new stories and updated global stories list.'
    }

print(clean_data())