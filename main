import requests
import time
import re
import os

TWITTERAPI_KEY  = "new1_f300b830a66e465e87523b975619d861"
X_USERNAME      = "cppfta"
TELEGRAM_TOKEN  = "8671050953:AAHyUny0bILBQyqlax7oL8jSGVp3gnroNBw"
TELEGRAM_CHAT   = "-1001369504484"

CHECK_EVERY_SECONDS = 5
LAST_TWEET_FILE     = "last_tweet_id.txt"

def load_last_tweet_id():
    if os.path.exists(LAST_TWEET_FILE):
        with open(LAST_TWEET_FILE, "r") as f:
            return f.read().strip()
    return None

def save_last_tweet_id(tweet_id):
    with open(LAST_TWEET_FILE, "w") as f:
        f.write(tweet_id)

def clean_tweet_text(text):
    text = re.sub(r'https://t\.co/\S+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

def get_latest_tweets():
    url = "https://api.twitterapi.io/twitter/user/last_tweets"
    headers = {"X-API-Key": TWITTERAPI_KEY}
    params  = {"userName": X_USERNAME}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        return data.get("tweets", [])
    except Exception as e:
        print(f"[ERROR] Failed to fetch tweets: {e}")
        return []

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        if result.get("ok"):
            print(f"[✓] Posted to Telegram: {text[:60]}...")
        else:
            print(f"[ERROR] Telegram rejected: {result}")
    except Exception as e:
        print(f"[ERROR] Failed to send to Telegram: {e}")

def filter_tweet(tweet):
    if tweet.get("text", "").startswith("RT @"):
        return False
    if tweet.get("isReply") and tweet.get("inReplyToUsername") != X_USERNAME:
        return False
    return True

def main():
    print("=" * 50)
    print("  X → Telegram Bot started!")
    print(f"  Monitoring: @{X_USERNAME}")
    print(f"  Checking every {CHECK_EVERY_SECONDS} seconds")
    print("=" * 50)

    last_id = load_last_tweet_id()

    if last_id is None:
        print("[INFO] First run — recording current latest tweet.")
        tweets = get_latest_tweets()
        if tweets:
            save_last_tweet_id(tweets[0]["id"])
        time.sleep(CHECK_EVERY_SECONDS)

    while True:
        tweets = get_latest_tweets()
        if tweets:
            last_id = load_last_twe
