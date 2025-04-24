import json
import os
import boto3

def process_data(cleaned_stories):
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

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    clean_bucket = os.environ['CLEAN_BUCKET']
    processed_bucket = os.environ['PROCESSED_BUCKET']
    clean_key = os.environ['CLEAN_KEY']
    processed_key = os.environ['PROCESSED_KEY']

    print(f"Reading from s3://{clean_bucket}/{clean_key}")
    response = s3.get_object(Bucket=clean_bucket, Key=clean_key)
    cleaned_data = json.loads(response['Body'].read())

    print(f"Processing {len(cleaned_data)} cleaned stories...")
    processed_summary = process_data(cleaned_data)

    print(f"Writing processed data to s3://{processed_bucket}/{processed_key}")
    s3.put_object(
        Bucket=processed_bucket,
        Key=processed_key,
        Body=json.dumps(processed_summary),
        ContentType='application/json'
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing complete'})
    }
