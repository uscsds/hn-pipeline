import json
import csv
import os
import boto3
from collections import Counter, defaultdict
from datetime import datetime
import re

s3 = boto3.client('s3')

def sentiment_analysis(cleaned_stories):
    sentiment_results = defaultdict(int)
    for story in cleaned_stories:
        text = story['text'] or story['title']
        polarity = float(story['sentiment'])
        if polarity > 0.05:
            sentiment = 'positive'
        elif polarity < -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        sentiment_results[sentiment] += 1
    return sentiment_results

def keyword_extraction(cleaned_stories, n):
    all_keywords = []
    for story in cleaned_stories:
        text = story['text'] or story['title']
        keywords = re.findall(r'\b\w{5,}\b', text.lower())
        all_keywords.extend(keywords)
    keyword_freq = Counter(all_keywords).most_common(n)
    return keyword_freq

def process_scores(cleaned_stories):
    score_summary = {
        'total_stories': 0,
        'total_score': 0,
        'average_score': 0,
        'top_stories': []
    }
    top_stories = sorted(cleaned_stories, key=lambda x: x['score'] or 0, reverse=True)[:10]
    score_summary['top_stories'] = top_stories

    total_score = sum(story['score'] or 0 for story in cleaned_stories)
    score_summary['total_stories'] = len(cleaned_stories)
    score_summary['total_score'] = total_score
    score_summary['average_score'] = total_score / len(cleaned_stories) if cleaned_stories else 0

    return score_summary

def analyze_stories(cleaned_stories):
    for story in cleaned_stories:
        story['textLength'] = len(story['text'])
        story['hour'] = datetime.utcfromtimestamp(story['time']).strftime('%Y-%m-%dT%H')

    return {
        'score_summary': process_scores(cleaned_stories),
        'sentiment_summary': sentiment_analysis(cleaned_stories),
        'top_keywords': keyword_extraction(cleaned_stories, 20),
        'stories': cleaned_stories,
    }

def extract_keywords(stories):
    return [kw[0] for kw in keyword_extraction(stories, 20)]

def get_day_bucket(timestamp_str):
    dt = datetime.fromisoformat(timestamp_str)
    return dt.strftime("%Y-%m-%d")

def aggregate_keywords_by_day(all_data):
    time_series = defaultdict(lambda: defaultdict(int))
    for stories in all_data:
        for story in stories:
            day = get_day_bucket(story["created_at"])
            keywords = extract_keywords([story])
            for kw in keywords:
                time_series[day][kw] += 1
    return sorted(
        [{"time": day, "keywords": dict(freq)} for day, freq in time_series.items()],
        key=lambda d: d["time"]
    )

def save_trend_csv(csv_path, trend_data, all_data):
    # Extract all unique keywords
    #for entry in trend_data:
    #    all_keywords.update(entry["keywords"].keys())
    top_keywords = [kw[0] for kw in keyword_extraction(all_data, 5)]
    top_keywords = sorted(top_keywords)

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["date"] + top_keywords)
        
        # Write each day
        for entry in trend_data:
            row = [entry["time"]] + [entry["keywords"].get(kw, 0) for kw in top_keywords]
            writer.writerow(row)

def load_json_from_s3(bucket, key):
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except s3.exceptions.NoSuchKey:
        print(f"No such file {key}, initializing empty.")
        return None
    except Exception as e:
        print(f"Failed to load {key}: {e}")
        return None

def lambda_handler(event, context):
    processed_bucket = os.environ['PROCESSED_BUCKET']
    processed_key = os.environ['PROCESSED_KEY_PREFIX']
    summary_state_file = os.environ['SUMMARY_STATE_FILE']

    # Load cleaned data file and summary state file
    clean_bucket = os.environ['CLEAN_BUCKET']
    record = event['Records'][0]
    clean_key = record['s3']['object']['key']
    cleaned_data = load_json_from_s3(Bucket=clean_bucket, Key=clean_key)
    summary_state = load_json_from_s3(summary_state_file) or {"last_processed": None, "processed_files": []}

    # Get timestamp for analysis result files and update summary state
    timestamp = "all"
    if not clean_key.__contains__("_all.json"):
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        summary_state.last_processed = timestamp
        summary_state.processed_files.append(timestamp)

    print(f"Analyzing {len(cleaned_data)} stories...")

    # Perform each analysis and store result in different files
    trend_data = aggregate_keywords_by_day(cleaned_data)
    save_trend_csv(f"analysis/keywork_trending_{timestamp}.csv", trend_data, cleaned_data)
    results = {
        f"analysis/stories_analysis_{timestamp}.json": analyze_stories(cleaned_data),
        summary_state_file: summary_state,
    }

    for key, result in results.items():
        print(f"Saving {key} to S3")
        s3.put_object(
            Bucket=processed_bucket,
            Key=key,
            Body=json.dumps(result),
            ContentType='application/json'
        )

    # Trigger additional workflows via EventBridge or S3 Event for specific analysis
    # Example: emit custom event or rely on S3 triggers set up in Terraform


    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'All analyses complete'})
    }