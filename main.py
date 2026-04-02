import requests
import time
import re
import os

TWITTERAPI_KEY  = "new1_f300b830a66e465e87523b975619d861"
TELEGRAM_TOKEN  = "8671050953:AAHyUny0bILBQyqlax7oL8jSGVp3gnroNBw"
TELEGRAM_CHAT   = "-1001369504484"

# Add as many X accounts as you want here!
X_USERNAMES = [
    "cryptoplusplus1",
    "KobeissiLetter",
]

CHECK_EVERY_SECONDS = 30

def load_last_id(username):
    path = f"/tmp/last_{username}.txt"
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
    except:
        pass
    return None

def save_last_id(username, tid):
    path = f"/tmp/last_{username}.txt"
    try:
        with open(path, "w") as f:
            f.write(str(tid))
    except Exception as e:
        print(f"Save error: {e}")

def clean_text(text):
    text = re.sub(r'https://t\.co/\S+', '', text)
    return text.strip()

def get_latest_tweets(username):
    try:
        url = "https://api.twitterapi.io/twitter/user/last_tweets"
        headers = {"X-API-Key": TWITTERAPI_KEY}
        params = {"userName": username}
        r = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"[{username}] Status: {r.status_code}")
        j = r.json()
        tweets = j.get("data", {}).get("tweets", [])
        print(f"[{username}] Found {len(tweets)} tweets")
        return tweets
    except Exception as e:
        print(f"[{username}] Fetch error: {e}")
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

print("Bot started! Monitoring: " + ", ".join(X_USERNAMES))

while True:
    for username in X_USERNAMES:
        try:
            tweets = get_latest_tweets(username)
            last_id = load_last_id(username)

            if tweets and last_id is None:
                save_last_id(username, tweets[0]["id"])
                print(f"[{username}] First run - saved ID: {tweets[0]['id']}")
            elif tweets:
                new = []
                for t in tweets:
                    if str(t["id"]) == str(last_id):
                        break
                    new.append(t)

                new.reverse()
                print(f"[{username}] New tweets: {len(new)}")

                for t in new:
                    txt = t.get("text", "")
                    if txt.startswith("RT @"):
                        continue
                    clean = clean_text(txt)
                    if clean:
                        send_telegram(clean)
                        time.sleep(2)

                if new:
                    save_last_id(username, tweets[0]["id"])

        except Exception as e:
            print(f"[{username}] Error: {e}")

        time.sleep(10)

    time.sleep(CHECK_EVERY_SECONDS)
