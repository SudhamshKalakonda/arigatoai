import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scrapy
from scrapy.crawler import CrawlerProcess
from pipeline.chunker import chunk_text
from pipeline.pinecone_client import upsert_chunks, get_index

ALL_RESULTS = []

SKIP_STARTS = ["javascript:", "#", "mailto:", "tel:", "void", "data:"]
SKIP_ENDS = [".pdf", ".xlsx", ".xls", ".doc", ".docx", ".zip", ".png", ".jpg"]

def parse_page(response, source, results):
    content_type = response.headers.get("Content-Type", b"").decode().lower()
    if "text/html" not in content_type:
        return
    title = response.css("title::text").get(default="").strip()
    content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
    text = " ".join(c.strip() for c in content if c.strip())
    if len(text) > 200:
        results.append({"url": response.url, "title": title, "text": text, "source": source})
        print(f"✓ {source.upper()}: {title[:50]} — {len(text)} chars")

def get_links(response):
    for href in response.css("a::attr(href)").getall():
        if not href:
            continue
        if any(href.startswith(x) for x in SKIP_STARTS):
            continue
        if any(href.lower().endswith(x) for x in SKIP_ENDS):
            continue
        yield response.follow(href, lambda r, h=href: None)

class GSTSpider(scrapy.Spider):
    name = "gst"
    start_urls = ["https://www.gst.gov.in/help/returns", "https://www.gst.gov.in/help/registration", "https://www.gst.gov.in/help/payments"]
    allowed_domains = ["gst.gov.in"]
    custom_settings = {"DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2, "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING", "HTTPERROR_ALLOW_ALL": True, "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "gst"})
            print(f"✓ GST: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in SKIP_STARTS): continue
            if any(href.lower().endswith(x) for x in SKIP_ENDS): continue
            yield response.follow(href, self.parse)

class EPFSpider(scrapy.Spider):
    name = "epf"
    start_urls = ["https://www.epfindia.gov.in/site_en/index.php"]
    allowed_domains = ["epfindia.gov.in"]
    custom_settings = {"DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2, "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING", "HTTPERROR_ALLOW_ALL": True, "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "epf"})
            print(f"✓ EPF: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in SKIP_STARTS): continue
            if any(href.lower().endswith(x) for x in SKIP_ENDS): continue
            yield response.follow(href, self.parse)

class TelanganaSpider(scrapy.Spider):
    name = "telangana_pt"
    start_urls = ["https://www.tgct.gov.in/tgportal/PT_Dashboard/PT_Home.aspx"]
    allowed_domains = ["tgct.gov.in"]
    custom_settings = {"DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2, "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING", "HTTPERROR_ALLOW_ALL": True, "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "telangana_pt"})
            print(f"✓ TS-PT: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in SKIP_STARTS): continue
            if any(href.lower().endswith(x) for x in SKIP_ENDS): continue
            yield response.follow(href, self.parse)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(GSTSpider)
    process.crawl(EPFSpider)
    process.crawl(TelanganaSpider)
    process.start()

    print(f"\nTotal pages scraped: {len(ALL_RESULTS)}")

    from collections import Counter
    sources = Counter(p["source"] for p in ALL_RESULTS)
    for src, count in sources.items():
        print(f"  {src}: {count} pages")

    with open("data/gov_pages.json", "w") as f:
        json.dump(ALL_RESULTS, f, indent=2)
    print("Saved to data/gov_pages.json")

    print("\nChunking and uploading to Pinecone...")
    all_chunks = []
    for page in ALL_RESULTS:
        chunks = chunk_text(text=page["text"], source_url=page["url"], title=page["title"], firm_id="arigato")
        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")
    upsert_chunks(all_chunks)

    stats = get_index().describe_index_stats()
    print(f"Total vectors in Pinecone: {stats['total_vector_count']}")
