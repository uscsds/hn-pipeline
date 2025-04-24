import json
import os
import boto3
from textblob import TextBlob
from collections import Counter, defaultdict
from datetime import datetime
import re

def sentiment_analysis(cleaned_stories):
    sentiment_results = []
    for story in cleaned_stories:
        text = story['text'] or story['title']
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        sentiment_results.append({
            'id': story['id'],
            'sentiment': sentiment
        })
    return sentiment_results

def keyword_extraction(cleaned_stories):
    all_keywords = []
    for story in cleaned_stories:
        text = story['text'] or story['title']
        keywords = re.findall(r'\b\w{5,}\b', text.lower())
        all_keywords.extend(keywords)
    keyword_freq = Counter(all_keywords).most_common(20)
    return keyword_freq

def trending_detection(cleaned_stories):
    hourly_count = defaultdict(int)
    for story in cleaned_stories:
        timestamp = story['time']
        hour = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H')
        hourly_count[hour] += 1
    return dict(sorted(hourly_count.items()))

def score_dynamics(cleaned_stories):
    dynamics = []
    for story in cleaned_stories:
        dynamics.append({
            'id': story['id'],
            'time': story['time'],
            'score': story['score'] or 0
        })
    return dynamics

def analyze_sentiment(text):
    if not text:
        return 'neutral'
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    return 'neutral'

def analyze_stories(cleaned_stories):
    sentiment_results = []
    all_keywords = []

    for story in cleaned_stories:
        text = story['text'] or story['title']
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        keywords = re.findall(r'\b\w{5,}\b', text.lower())  # simple keyword extraction

        sentiment_results.append({
            'id': story['id'],
            'sentiment': sentiment
        })
        all_keywords.extend(keywords)

    keyword_freq = Counter(all_keywords).most_common(20)

    return {
        'sentiment_summary': sentiment_results,
        'top_keywords': keyword_freq
    }

def title_length_distribution(cleaned_stories):
    return [len(story['title']) for story in cleaned_stories if story['title']]


def comment_count_analysis(cleaned_stories):
    return [{'id': story['id'], 'descendants': story.get('descendants', 0)} for story in cleaned_stories]


def lambda_handler(event, context):
    s3 = boto3.client('s3')

    processed_bucket = os.environ['PROCESSED_BUCKET']
    analysis_bucket = os.environ['ANALYSIS_BUCKET']
    processed_key = os.environ['PROCESSED_KEY']
    analysis_key = os.environ['ANALYSIS_KEY']

    print(f"Reading processed stories from s3://{processed_bucket}/{processed_key}")
    response = s3.get_object(Bucket=processed_bucket, Key=processed_key)
    processed_data = json.loads(response['Body'].read())
    stories = processed_data.get('top_stories', [])

    sentiment_counts = Counter()
    keyword_counts = Counter()

    for story in stories:
        sentiment = analyze_sentiment(story.get('text'))
        sentiment_counts[sentiment] += 1

        title = story.get('title', '')
        words = [word.lower() for word in title.split() if len(word) > 3]
        keyword_counts.update(words)

    analysis_summary = {
        'sentiment': dict(sentiment_counts),
        'top_keywords': keyword_counts.most_common(10)
    }

    print(f"Writing analysis to s3://{analysis_bucket}/{analysis_key}")
    s3.put_object(
        Bucket=analysis_bucket,
        Key=analysis_key,
        Body=json.dumps(analysis_summary),
        ContentType='application/json'
    )

    # More analysis
    clean_bucket = os.environ['CLEAN_BUCKET']
    clean_key = os.environ['CLEAN_KEY']

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")

    response = s3.get_object(Bucket=clean_bucket, Key=clean_key)
    cleaned_data = json.loads(response['Body'].read())

    print(f"Analyzing {len(cleaned_data)} stories...")

    # Perform each analysis and store result in different files
    results = {
        f"analysis/sentiment_analysis_{timestamp}.json": sentiment_analysis(cleaned_data),
        f"analysis/keyword_extraction_{timestamp}.json": keyword_extraction(cleaned_data),
        f"analysis/trending_detection_{timestamp}.json": trending_detection(cleaned_data),
        f"analysis/score_dynamics_{timestamp}.json": score_dynamics(cleaned_data),
        f"analysis/title_length_distribution_{timestamp}.json": title_length_distribution(cleaned_data),
        f"analysis/comment_count_analysis_{timestamp}.json": comment_count_analysis(cleaned_data),
    }

    for key, result in results.items():
        print(f"Saving {key} to S3")
        s3.put_object(
            Bucket=analysis_bucket,
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