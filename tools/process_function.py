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

def load_cleaned_filepaths(data_folder):
    all_files = glob.glob(os.path.join(data_folder, "*cleaned_*.json"))
    return all_files

def load_json_file(data_path):
    print('Loading json file: ' + data_path)
    try:
        with open(data_path, "r") as f:
            return json.load(f)
    except:
        return None

def load_cleaned_files(data_folder):
    all_files = glob.glob(os.path.join(data_folder, "*cleaned_*.json"))
    for file in all_files:
        with open(file, "r") as f:
            yield json.load(f)

def save_json_file(output_path, data):
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

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

def save_trend_csv(csv_path, trend_data, all_data):
    # Extract all unique keywords
    #for entry in trend_data:
    #    all_keywords.update(entry["keywords"].keys())
    #top_keywords = [kw[0] for kw in keyword_extraction(all_data, 10)]
    top_keywords = [kw[0] for kw in extract_topics(all_data, 10)]
    top_keywords = sorted(top_keywords)
    print("TREND: ")
    print(trend_data)
    print("TOP KEYWORDS:")
    print(top_keywords)

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["date"] + top_keywords)
        
        # Write each day
        for entry in trend_data:
            row = [entry["time"]] + [entry["keywords"].get(kw, 0) for kw in top_keywords]
            writer.writerow(row)
    
def load_cleaned_files(data_folder):
    all_files = glob.glob(os.path.join(data_folder, "cleaned_*.json"))
    for file in all_files:
        with open(file, "r") as f:
            yield json.load(f)

def process_data():
    processed_bucket = "processed/"
    processed_key_prefix = "processed/hn_top_processed"
    summary_state_file = "state/processed_files.json"
    clean_bucket = "cleaned/"
    clean_key_prefix = "cleaned/hn_top_cleaned"

    # Read raw HN dump file and process cleanning
    for filepath in load_cleaned_filepaths(clean_bucket):
        key = re.sub(clean_key_prefix + "_", "", filepath)
        timestampstr = re.sub(".json", "", key)
        # Load cleaned data file and summary state file       
        cleaned_data = load_json_file(filepath) or []
        summary_state = load_json_file(summary_state_file) or {"last_processed": None, "processed_files": []}

        # Get timestamp for analysis result files and update summary state
        timestamp = "all"
        if not filepath.__contains__("_all.json"):
            timestamp = str(datetime.fromtimestamp(int(timestampstr)))
            #timestamp = datetime.strptime(str(datetime_object), "%Y-%m-%dT%H-%M-%S")
            summary_state["last_processed"] = timestamp
            summary_state["processed_files"].append(timestamp)

        print(f"Analyzing {len(cleaned_data)} stories...")

        # Perform each analysis and store result in different files
        trend_data = aggregate_keywords_by_day(cleaned_data)
        save_trend_csv(f"analysis/keywork_trending_{timestamp}.csv", trend_data, cleaned_data)
        results = {
            f"analysis/stories_analysis_{timestamp}.json": analyze_stories(cleaned_data),
            summary_state_file: summary_state,
        }

        for key, result in results.items():
            save_json_file(key, result)

        # Trigger additional workflows via EventBridge or S3 Event for specific analysis
        # Example: emit custom event or rely on S3 triggers set up in Terraform


    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'All analyses complete'})
    }

print(process_data())