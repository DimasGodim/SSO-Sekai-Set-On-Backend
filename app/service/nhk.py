import feedparser
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from data.act.base import save_news, news_list
from data.db.mongo.models import News
def get_full_nhk_content(link: str) -> str:
    try:
        response = requests.get(link, timeout=5)
        response.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("div", class_="content--summary") or soup.find("div", class_="article-main")
    if not container:
        return ""

    paragraphs = container.find_all("p")
    return "\n".join(p.get_text(strip=True) for p in paragraphs if p.text).strip()

async def fetch_nhk_news():
    rss_url = "https://www3.nhk.or.jp/rss/news/cat0.xml"
    feed = feedparser.parse(rss_url)

    news = await news_list()
    existing_links = {row["link"] for row in news}

    new_entries = 0

    for entry in feed.entries:
        if entry.link in existing_links:
            continue  # Skip kalau sudah ada

        full_content = get_full_nhk_content(entry.link)

        news = {
            "title": entry.title,
            "link": entry.link,
            "published_at": datetime(*entry.published_parsed[:6]),
            "summary": entry.get("summary", ""),
            "content": full_content,
        }

        await save_news(data=news)
        new_entries += 1

    if new_entries:
        print(f"{new_entries} berita baru berhasil ditambahkan.")
    else:
        print("ℹTidak ada berita baru.")


scheduler = BackgroundScheduler()
async def start_news_fetcher():
    async def job():
            print("[Scheduler] Fetching NHK News...")
            await fetch_nhk_news()

    await job()
    
    scheduler.add_job(job, "interval", hours=2)
    scheduler.start()
    print(f"[{datetime.now().isoformat()}] NHK news updated.")
