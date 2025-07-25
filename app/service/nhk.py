import feedparser
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from app.db.models import News
from app.db.database import SessionLocal

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

def fetch_nhk_news(db):
    rss_url = "https://www3.nhk.or.jp/rss/news/cat0.xml"
    feed = feedparser.parse(rss_url)

    # Ambil semua link yang sudah ada di DB sekali saja (efisien)
    existing_links = {
        row.link for row in db.query(News.link).all()
    }

    new_entries = 0

    for entry in feed.entries:
        if entry.link in existing_links:
            continue  # Skip kalau sudah ada

        full_content = get_full_nhk_content(entry.link)

        news = News(
            title=entry.title,
            link=entry.link,
            published_at=datetime(*entry.published_parsed[:6]),
            summary=entry.get("summary", ""),
            content=full_content,
            source="NHK"
        )

        db.add(news)
        new_entries += 1

    if new_entries:
        db.commit()
        print(f"{new_entries} berita baru berhasil ditambahkan.")
    else:
        print("ℹTidak ada berita baru.")


scheduler = BackgroundScheduler()
def start_news_fetcher():
    def job():
        db = SessionLocal()
        try:
            print("[Scheduler] Fetching NHK News...")
            fetch_nhk_news(db)
        finally:
            db.close()

    job()
    
    scheduler.add_job(job, "interval", hours=2)
    scheduler.start()
    print(f"[{datetime.now().isoformat()}] 6NHK news updated.")
