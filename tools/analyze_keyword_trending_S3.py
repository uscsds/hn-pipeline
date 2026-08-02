import os
import json
import glob
import csv
import boto3
from collections import defaultdict
from datetime import datetime

s3_client = boto3.client('s3')

def load_cleaned_files(data_folder):
    all_files = glob.glob(os.path.join(data_folder, "cleaned_*.json"))
    for file in all_files:
        with open(file, "r") as f:
            yield json.load(f)

def extract_keywords(stories):
    return [word.lower() for story in stories for word in story["title"].split()]

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

def save_trend_json(output_path, trend_data):
    with open(output_path, "w") as f:
        json.dump(trend_data, f, indent=2)

def save_trend_csv(csv_path, trend_data):
    # Extract all unique keywords
    all_keywords = set()
    for entry in trend_data:
        all_keywords.update(entry["keywords"].keys())
    all_keywords = sorted(all_keywords)

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["date"] + all_keywords)
        
        # Write each day
        for entry in trend_data:
            row = [entry["time"]] + [entry["keywords"].get(kw, 0) for kw in all_keywords]
            writer.writerow(row)

def upload_to_s3(file_path, bucket, s3_key):
    s3_client.upload_file(file_path, bucket, s3_key)
    print(f"Uploaded {file_path} to s3://{bucket}/{s3_key}")

# Usage
if __name__ == "__main__":
    input_dir = "cleaned_data/"
    output_json = "keywords_trend_all.json"
    output_csv = "keywords_trend_all.csv"
    s3_bucket = "YOUR_BUCKET_NAME"
    s3_json_key = "analysis/keywords_trend_all.json"
    s3_csv_key = "analysis/keywords_trend_all.csv"

    all_cleaned = list(load_cleaned_files(input_dir))
    trend = aggregate_keywords_by_day(all_cleaned)

    # Save to local files
    save_trend_json(output_json, trend)
    save_trend_csv(output_csv, trend)

    # Upload both to S3
    upload_to_s3(output_json, s3_bucket, s3_json_key)
    upload_to_s3(output_csv, s3_bucket, s3_csv_key)
