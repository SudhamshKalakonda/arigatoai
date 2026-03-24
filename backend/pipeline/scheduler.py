import os
import json
import hashlib
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEN_HASHES_FILE = "data/seen_hashes.json"

def load_seen_hashes() -> set:
    if os.path.exists(SEEN_HASHES_FILE):
        with open(SEEN_HASHES_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen_hashes(hashes: set):
    with open(SEEN_HASHES_FILE, "w") as f:
        json.dump(list(hashes), f)

def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def run_weekly_update():
    logger.info(f"Starting weekly knowledge update at {datetime.now()}")

    from pipeline.spiders.incometax_spider import run_incometax_spider
    from pipeline.spiders.gst_spider import run_gst_spider
    from pipeline.chunker import chunk_text
    from pipeline.pinecone_client import upsert_chunks

    seen_hashes = load_seen_hashes()
    new_pages = []

    logger.info("Scraping incometax.gov.in...")
    try:
        pages = run_incometax_spider()
        for page in pages:
            h = get_text_hash(page["text"])
            if h not in seen_hashes:
                new_pages.append(page)
                seen_hashes.add(h)
        logger.info(f"incometax.gov.in: {len(pages)} pages, {len(new_pages)} new")
    except Exception as e:
        logger.error(f"incometax scrape failed: {e}")

    logger.info("Scraping gst.gov.in...")
    try:
        pages = run_gst_spider()
        for page in pages:
            h = get_text_hash(page["text"])
            if h not in seen_hashes:
                new_pages.append(page)
                seen_hashes.add(h)
        logger.info(f"gst.gov.in: {len(pages)} pages")
    except Exception as e:
        logger.error(f"gst scrape failed: {e}")

    if new_pages:
        logger.info(f"Chunking and indexing {len(new_pages)} new pages...")
        all_chunks = []
        for page in new_pages:
            chunks = chunk_text(
                text=page["text"],
                source_url=page["url"],
                title=page["title"],
                firm_id="arigato"
            )
            all_chunks.extend(chunks)

        upsert_chunks(all_chunks)
        save_seen_hashes(seen_hashes)
        logger.info(f"Weekly update complete. Added {len(all_chunks)} new chunks.")
    else:
        logger.info("No new content found. Knowledge base is up to date.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_weekly_update,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly_update",
        name="Weekly knowledge update",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started. Weekly update every Monday at 9am.")
    return scheduler