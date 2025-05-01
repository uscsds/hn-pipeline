import json
import csv
import os
import glob
from collections import Counter, defaultdict
from datetime import datetime, timezone
import re
import spacy
from nltk.corpus import stopwords
# Make sure to load properly if custom path (only if needed)
# nlp = spacy.load("/opt/python/spacy_data/en_core_web_sm")

# Normal way (if installed right):
nlp = spacy.load("en_core_web_sm")

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

""" def keyword_extraction(cleaned_stories, n):
    all_keywords = []
    stop_words = set(stopwords.words('english'))
    stop_words.update([
        'like', 'good', 'really', 'new', 'just', 'even', 'something', 'things', 
        'using', 'used', 'many', 'much', 'way', 'make', 'also', 'get', 'still', 
        'one', 'two', 'first', 'second', 'lot', 'time', 'see', 'know', 'want',
        'date', 'com', 'open', 'quot', 'use', 'making'
    ])
    for story in cleaned_stories:
        # Tokenize: keep only words, no symbols
        text = story['text'] or story['title']
        blob = TextBlob(text)
        words = [word.lower() for word in blob.noun_phrases if word.lower() not in stopwords]
        #words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        all_keywords.extend(words)
    keyword_freq = Counter(all_keywords).most_common(n)
    return  keyword_freq"""

def keyword_extraction(cleaned_stories, n):
    all_keywords = []
    stop_words = set(stopwords.words('english'))
    stop_words.update([
        'like', 'good', 'really', 'new', 'just', 'even', 'something', 'things', 
        'using', 'used', 'many', 'much', 'way', 'make', 'also', 'get', 'still', 
        'one', 'two', 'first', 'second', 'lot', 'time', 'see', 'know', 'want',
        'date', 'com', 'open', 'quot', 'use', 'making', '\'s'
    ]) 
    for story in cleaned_stories:
        # Tokenize: keep only words, no symbols
        text = story['text'] or story['title']
        doc = nlp(text)
        keywords = []
        for token in doc:
            if token.is_stop or token.is_punct or token.is_space or token.text in stop_words:
                continue
            if token.pos_ in {"NOUN", "PROPN", "ADJ"}:  # Only important parts
                keywords.append(token.lemma_.lower())  # Lemmatize and lowercase
        all_keywords.extend(keywords)
    if n == -1:
        keyword_freq = Counter(all_keywords).most_common(len(all_keywords))
    else: 
        keyword_freq = Counter(all_keywords).most_common(n)
    return  keyword_freq

def get_keywords(stories, n):
    return [key for key, freq in keyword_extraction(stories, n)]

def remove_stop_words(nound_chunks):
    result_chunks = []
  
    for chunk in nound_chunks:
        # check if the chunk contains at least one non-stopword token
        if any(not (token.is_stop or token.is_punct or token.is_space)
               and token.pos_ in {"NOUN", "PROPN", "ADJ"}  for token in chunk):
            result_chunks.append(chunk)
    return result_chunks

def extract_topics(stories, top_n=10):
    topics = defaultdict(int)

    for story in stories:
        noun_phrases = []
        kw_fr = keyword_extraction([story], -1)
        print("Story keywords:")
        print(kw_fr)
        ph_fr = defaultdict(int)
        # Extract noun chunks
        doc = nlp(story['title']) #+ ' ' + story['text'])
        for chunk in doc.noun_chunks:
            count = 0
            # check if the chunk contains at least one non-stopword token
            if any(not (token.is_stop or token.is_punct or token.is_space)
                and token.pos_ in {"NOUN", "PROPN", "ADJ"}  for token in chunk):
                # calculate frequency of chunk based on frequency of all its child tokens
                for token in chunk:
                    getcount = [fr for kw, fr in kw_fr if kw in token.text]
                    count += getcount[0] if len(getcount) > 0 else 0
                ph_fr[chunk.text] = count
                topics[chunk.text] += count 
        print("Story:")
        print(ph_fr)
        #noun_phrases = [ph for ph in list(dict(sorted(ph_fr.items(), key=lambda x: x[1] or 0, reverse=True)))[:top_n]]
        #topics = [{"topic": phrase, "count": count} for phrase, count in common_phrases]
        #topics.extend(noun_phrases)
        #topics.update(ph_fr)
    #counter = Counter(topics)
    #return counter.most_common(top_n)
    print(topics)
    freq = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:top_n]
    print("Top phrases:")
    print(freq)
    return freq

def process_scores(cleaned_stories):
    score_summary = {
        'total_stories': 0,
        'total_score': 0,
        'average_score': 0,
        'top_stories': []
    }
    # Select top stories based on comments size and score
    #top_stories = sorted(cleaned_stories, key=lambda x: x['score'] or 0, reverse=True)[:10]
    top_stories = sorted(cleaned_stories, key=lambda x: x['kidsSize'] or 0, reverse=True)[:10]
    top_ids = [story['id'] for story in top_stories]
    top_scores = sorted(cleaned_stories, key=lambda x: x['score'] or 0, reverse=True)[:10]
    for story in top_scores:
        if story['id'] not in top_ids:
            top_stories.append(story)

    score_summary['top_stories'] = top_stories

    total_score = sum(story['score'] or 0 for story in cleaned_stories)
    score_summary['total_stories'] = len(cleaned_stories)
    score_summary['total_score'] = total_score
    score_summary['average_score'] = total_score / len(cleaned_stories) if cleaned_stories else 0

    return score_summary

def analyze_stories(cleaned_stories):
    for story in cleaned_stories:
        story['textLength'] = len(story['text'])
        story['hour'] = datetime.fromtimestamp(float(story['time']), tz=timezone.utc).strftime('%H')
        story['keywords'] = [kw[0] for kw in extract_topics([story], 5)]

    return {
        'score_summary': process_scores(cleaned_stories),
        'sentiment_summary': sentiment_analysis(cleaned_stories),
        #'top_keywords': keyword_extraction(cleaned_stories, 20),
        'top_keywords': extract_topics(cleaned_stories, 10),
        'stories': cleaned_stories,
    }

def extract_keywords(stories):
    return [kw[0] for kw in keyword_extraction(stories, 20)]

def get_day_bucket(timestamp_str):
    dt = datetime.fromtimestamp(int(timestamp_str))
    return dt.strftime("%Y-%m-%d")

def aggregate_keywords_by_day(all_data):
    time_series = defaultdict(lambda: defaultdict(int))
    for story in all_data:
        day = get_day_bucket(story["time"])
        #keywords = extract_keywords([story])
        keywords = [k for k, f in extract_topics([story])]
        for kw in keywords:
            time_series[day][kw] += 1
    return sorted(
        [{"time": day, "keywords": dict(freq)} for day, freq in time_series.items()],
        key=lambda d: d["time"]
    )


def get_trend_csv_buffer(trend_data, all_data):
    # Extract all unique keywords
    #for entry in trend_data:
    #    all_keywords.update(entry["keywords"].keys())
    csv_buffer = io.StringIO()
    top_keywords = [kw[0] for kw in extract_topics(all_data, 10)]
    top_keywords = sorted(top_keywords)
    fieldnames = ["date"] + top_keywords

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
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
    state_bucket = os.environ['STATE_BUCKET']
    summary_state_file = os.environ['SUMMARY_STATE_FILE']
    clean_key_prefix = os.environ['CLEAN_KEY_PREFIX']

    # Load cleaned data file and summary state file
    clean_bucket = os.environ['CLEAN_BUCKET']
    record = event['Records'][0]
    clean_key = record['s3']['object']['key']
    cleaned_data = load_json_from_s3(Bucket=clean_bucket, Key=clean_key) or []
    summary_state = load_json_from_s3(state_bucket, summary_state_file) or {"last_processed": None, "processed_files": []}

    # Get timestamp for analysis result files and update summary state
    timestamp = "all"
    postfix = re.sub(clean_key_prefix + "_", "", clean_key)
    timestampstr = re.sub(".json", "", postfix)
    if not clean_key.__contains__("_all.json"):
        #timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        timestamp = str(datetime.fromtimestamp(int(timestampstr)))
        summary_state["last_processed"] = timestamp
        summary_state["processed_files"].append(timestamp)
        summary_state.last_processed = timestamp
        summary_state.processed_files.append(timestamp)
    else:
        if "all" in summary_state["processed_files"]:
            summary_state["processed_files"].remove("all")
        summary_state["processed_files"].append("all")

    print(f"Analyzing {len(cleaned_data)} stories...")

    # Perform each analysis and store result in different files
    trend_data = aggregate_keywords_by_day(cleaned_data)
    csv_buffer = get_trend_csv_buffer(trend_data, cleaned_data)
    # Upload csv file to S3
    s3.put_object(
        Bucket=processed_bucket,
        Key=f"analysis/keywork_trending_{timestamp}.csv",
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )

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