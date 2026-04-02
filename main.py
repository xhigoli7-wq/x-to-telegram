import requests
import time
import re
import os

TWITTERAPI_KEY  = "new1_f300b830a66e465e87523b975619d861"
X_USERNAME      = "cryptoplusplus1"
TELEGRAM_TOKEN  = "8671050953:AAHyUny0bILBQyqlax7oL8jSGVp3gnroNBw"
TELEGRAM_CHAT   = "-1001369504484"

CHECK_EVERY_SECONDS = 10
LAST_TWEET_FILE     = "last_tweet_id.txt"

def load_last_tweet_id():
    try:
        if os.path.exists(LAST_TWEET_FILE):
            with open(LAST_TWEET_FILE, "r") as f:
                return f.read().strip()
    except:
        pass
    return None

def save_last_tweet_id(tweet_id):
    try:
        with open(LAST_TWEET_FILE, "w") as f:
            f.write(tweet_id)
    except Exception as e:
        print(f"[ERROR] Could not save tweet ID: {e}")

def clean_tweet_text(text):
    text = re.sub(r'https://t\.co/\S+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def get_latest_tweets():
    try:
        url = "https://api.twitterapi.io/twitter/user/last_tweets"
        headers = {"X-API-Key": TWITTERAPI_KEY}
        params  = {"userName": X_USERNAME}
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"[API] Status: {response.status_code}")
        data = response.json()
        print(f"[API] Response: {str(data)[:200]}")
        return data.get("tweets", [])
    except Exception as e:
        print(f"[ERROR] Fetch failed: {e}")
        return []

def send_to_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT, "text": text}
        response = requests.post(url, json=payload, timeout=15)
        result = response.json()
        if result.get("ok"):
            print(f"[✓] Sent to Telegram!")
        else:
            print(f"[ERROR] Telegram: {result}")
    except Exception as e:
        print(f"[ERROR] Telegram failed: {e}")

def filter_tweet(tweet):
    if tweet.get("text", "").startswith("RT @"):
        return False
    if tweet.get("isReply") and tweet.get("inReplyToUsername") != X_USERNAME:
        return False
    return True

print("==================================================")
print("  X → Telegram Bot started!")
print(f"  Monitoring: @{X_USERNAME}")
print("==================================================")

last_id = load_last_tweet_id()

if last_id is None:
    print("[INFO] First run — saving latest tweet ID...")
    tweets = get_latest_tweets()
    if tweets:
        save_last_tweet_id(tweets[0]["id"])
        print(f"[INFO] Saved ID: {tweets[0]['id']}")
    else:
        print("[INFO] No tweets found on first run")

while True:
    try:
        print(f"[CHECK] Fetching tweets...")
        tweets = get_latest_tweets()
        if tweets:
            last_id = load_last_tweet_id()
            new_tweets = []
            for tweet in tweets:
                if tweet["id"] == last_id:
                    break
                new_tweets.append(tweet)

            new_tweets.reverse()
            print(f"[INFO] Found {len(new_tweets)} new tweet(s)")

            for tweet in new_tweets:
                if filter_tweet(tweet):
                    clean_text = clean_tweet_text(tweet["text"])
                    if clean_text:
                        send_to_telegram(clean_text)
                        time.sleep(1)

            if new_tweets:
                save_last_tweet_id(tweets[0]["id"])
        else:
            print("[INFO] No tweets returned")

    except Exception as e:
        print(f"[ERROR] Loop error: {e}")

    time.sleep(CHECK_EVERY_SECONDS)
