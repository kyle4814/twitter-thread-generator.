import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REDDIT_API_URL = "https://api.pushshift.io/reddit/search/submission/?subreddit={}&limit=5"

def fetch_reddit_posts(subreddit, keywords):
    """Fetch top Reddit posts and filter by keywords."""
    headers = {"User-Agent": "ThreadGeneratorBot"}
    response = requests.get(REDDIT_API_URL.format(subreddit), headers=headers)

    if response.status_code != 200:
        print(f"Error fetching subreddit {subreddit}: {response.status_code}")
        return []

    try:
        posts = response.json().get("data", {}).get("children", [])
    except Exception as e:
        print(f"Error parsing JSON from {subreddit}: {e}")
        return []

    relevant_posts = []
    for post in posts:
        title = post["data"].get("title", "")
        if any(keyword.lower() in title.lower() for keyword in keywords):
            relevant_posts.append(title)

    print(f"Fetched {len(relevant_posts)} posts from {subreddit} matching keywords {keywords}")
    return relevant_posts

@app.route('/generate_thread', methods=['POST'])
def generate_thread():
    data = request.json
    topic = data.get("topic", "Entrepreneurship")
    subreddits = data.get("subreddits", ["technology", "business"])
    keywords = data.get("keywords", ["AI", "automation", "startup"])
    num_threads = int(data.get("num_threads", 1))
    thread_length = int(data.get("thread_length", 5))

    threads = []
    for i in range(num_threads):
        thread_posts = []

        for subreddit in subreddits:
            posts = fetch_reddit_posts(subreddit, keywords)
            if posts:
                thread_posts.extend(posts[:thread_length])

        if not thread_posts:
            thread_posts = [f"🔥 {topic} Insight {j+1}" for j in range(thread_length)]  # Fallback if no data found

        threads.append(thread_posts)

    return jsonify({"threads": threads})

if __name__ == '__main__':
    app.run(debug=True)
