# Script for Scrapping and Saving the Data

from pathlib import Path
import requests, json, time

def load_markdown_chunks(folder, chunk_size=512):
    chunks = []
    for file in Path(folder).rglob("*.md"):
        text = file.read_text()
        for i in range(0, len(text), chunk_size):
            chunks.append({"content": text[i:i+chunk_size], "source": str(file)})
    return chunks

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Cookie': 'from-your-browser',
    'Discourse-Logged-In': 'true',
    'Discourse-Present': 'true',
    'X-Csrf-Token': 'from-your-browser',
}


def scrape_discourse(category=34, start="2025-01-01", end="2025-04-14"):
    page, all_posts = 0, []
    while True:
        url = f"https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/{category}.json?page={page}"
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"Failed to fetch page {page}, status code: {resp.status_code}")
            break
        topics = resp.json().get("topic_list", {}).get("topics", [])
        if not topics:
            break
        for topic in topics:
            created = topic["created_at"][:10]
            if start <= created <= end:
                tid = topic["id"]
                slug = topic["slug"]
                post_url = f"https://discourse.onlinedegree.iitm.ac.in/t/{slug}/{tid}.json"
                post_data = requests.get(post_url, headers=HEADERS).json()
                for post in post_data["post_stream"]["posts"]:
                    all_posts.append({
                        "content": post["cooked"],
                        "source": f"https://discourse.onlinedegree.iitm.ac.in/t/{slug}/{tid}/{post['post_number']}"
                    })
        page += 1
        time.sleep(1)
    with open("../data/discourse.json", "w") as f:
        json.dump(all_posts, f)

# if __name__ == '__main__':
#     scrape_discourse()
