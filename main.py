import requests
import time
import re
import os

TWITTERAPI_KEY  = "new1_f300b830a66e465e87523b975619d861"
X_USERNAME      = "cryptoplusplus1"
TELEGRAM_TOKEN  = "8671050953:AAHyUny0bILBQyqlax7oL8jSGVp3gnroNBw"
TELEGRAM_CHAT   = "-1001369504484"

CHECK_EVERY_SECONDS = 15
LAST_TWEET_FILE = "/tmp/last_tweet_id.txt"

def load_last_id():
    try:
        if os.path.exists(LAST_TWEET_FILE):
            with open(LAST_TWEET_FILE, "r") as f:
                return f.read().strip()
    except:
        pass
    return None

def save_last_id(tid):
    try:
        with open(LAST_TWEET_FILE, "w") as f:
            f.write(str(tid))
    except Exception as e:
        print(f"Save error: {e}")

def clean_text(text):
    text = re.sub(r'https://t\.co/\S+', '', text)
    return text.strip()

def get_latest_tweets():
    try:
        url = "https://api.twitterapi.io/twitter/user/last_tweets"
        headers = {"X-API-Key": TWITTERAPI_KEY}
        params = {"userName": X_USERNAME}
        r = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"Status: {r.status_code}")
        j = r.json()
        tweets = j.get("data", {}).get("tweets", [])
        print(f"Found {len(tweets)} tweets")
        if tweets:
            print(f"Latest ID: {tweets[0]['id']}")
        return tweets
    except Exception as e:
        print(f"Fetch error: {e}")
        return []

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT, "text": text}, timeout=15)
        result = r.json()
        if result.get("ok"):
            print(f"Sent to Telegram!")
        else:
            print(f"Telegram error: {result}")
    except Exception as e:
        print(f"Telegram error: {e}")

print("Bot started! Monitoring @" + X_USERNAME)

last_id = load_last_id()

while True:
    try:
        tweets = get_latest_tweets()

        if tweets and last_id is None:
            last_id = tweets[0]["id"]
            save_last_id(last_id)
            print(f"First run - saved ID: {last_id}")
        elif tweets:
            new = []
            for t in tweets:
                if str(t["id"]) == str(last_id):
                    break
                new.append(t)

            new.reverse()
            print(f"New tweets: {len(new)}")

            for t in new:
                txt = t.get("text", "")
                if txt.startswith("RT @"):
                    continue
                clean = clean_text(txt)
                if clean:
                    send_telegram(clean)
                    time.sleep(2)

            if new:
                last_id = tweets[0]["id"]
                save_last_id(last_id)

    except Exception as e:
        print(f"Loop error: {e}")

    time.sleep(CHECK_EVERY_SECONDS)
