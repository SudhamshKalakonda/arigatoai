import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scrapy
from scrapy.crawler import CrawlerProcess
from pipeline.chunker import chunk_text
from pipeline.pinecone_client import upsert_chunks, get_index
ALL_RESULTS = []

class GSTSpider(scrapy.Spider):
    name = "gst"
    start_urls = [
        "https://www.gst.gov.in/help/returns",
        "https://www.gst.gov.in/help/registration",
        "https://www.gst.gov.in/help/payments",
    ]
    allowed_domains = ["gst.gov.in"]
    custom_settings = {
        "DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
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
            if not href or any(href.startswith(x) for x in ["javascript:", "#", "mailto:", "tel:"]):
                continue
            if any(href.lower().endswith(x) for x in [".pdf", ".xlsx", ".xls", ".doc", ".zip"]):
                continue
            yield response.follow(href, self.parse)

class MCASpider(scrapy.Spider):
    name = "mca"
    start_urls = [
        "https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/acts.html",
        "https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/rules.html",
    ]
    allowed_domains = ["mca.gov.in"]
    custom_settings = {
        "DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "mca"})
            print(f"✓ MCA: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in ["javascript:", "#", "mailto:", "tel:"]):
                continue
            if any(href.lower().endswith(x) for x in [".pdf", ".xlsx", ".xls", ".doc", ".zip"]):
                continue
            yield response.follow(href, self.parse)

class ICAISpider(scrapy.Spider):
    name = "icai"
    start_urls = [
        "https://www.icai.org/post.html?post_id=10289",
        "https://www.icai.org/new_post.html?post_id=15013",
    ]
    allowed_domains = ["icai.org"]
    custom_settings = {
        "DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "icai"})
            print(f"✓ ICAI: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in ["javascript:", "#", "mailto:", "tel:"]):
                continue
            if any(href.lower().endswith(x) for x in [".pdf", ".xlsx", ".xls", ".doc", ".zip"]):
                continue
            yield response.follow(href, self.parse)

class CBICSpider(scrapy.Spider):
    name = "cbic"
    start_urls = [
        "https://www.cbic.gov.in/htdocs-cbec/gst/index",
    ]
    allowed_domains = ["cbic.gov.in"]
    custom_settings = {
        "DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "cbic"})
            print(f"✓ CBIC: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in ["javascript:", "#", "mailto:", "tel:"]):
                continue
            if any(href.lower().endswith(x) for x in [".pdf", ".xlsx", ".xls", ".doc", ".zip"]):
                continue
            yield response.follow(href, self.parse)
class EPFSpider(scrapy.Spider):
    name = "epf"
    start_urls = [
        "https://www.epfindia.gov.in/site_hi/index.php",
        "https://www.epfindia.gov.in/site_en/index.php",
    ]
    allowed_domains = ["epfindia.gov.in"]
    custom_settings = {
        "DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
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
            if not href or any(href.startswith(x) for x in ["javascript:", "#", "mailto:", "tel:"]):
                continue
            if any(href.lower().endswith(x) for x in [".pdf", ".xlsx", ".xls", ".doc", ".zip"]):
                continue
            yield response.follow(href, self.parse)

class ESICSpider(scrapy.Spider):
    name = "esic"
    start_urls = [
        "https://esic.gov.in/",
    ]
    allowed_domains = ["esic.gov.in"]
    custom_settings = {
        "DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "VERIFY": False,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "DOWNLOADER_CLIENTCONTEXTFACTORY": "scrapy.core.downloader.contextfactory.BrowserLikeContextFactory",
    }
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "esic"})
            print(f"✓ ESIC: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in ["javascript:", "#", "mailto:", "tel:"]):
                continue
            if any(href.lower().endswith(x) for x in [".pdf", ".xlsx", ".xls", ".doc", ".zip"]):
                continue
            yield response.follow(href, self.parse)

class TelanganaGSTSpider(scrapy.Spider):
    name = "telangana_pt"
    start_urls = [
        "https://www.tgct.gov.in/tgportal/PT_Dashboard/PT_Home.aspx",
    ]
    allowed_domains = ["tgct.gov.in"]
    custom_settings = {
        "DEPTH_LIMIT": 2, "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False, "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return
        title = response.css("title::text").get(default="").strip()
        content = response.css("p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text").getall()
        text = " ".join(c.strip() for c in content if c.strip())
        if len(text) > 200:
            ALL_RESULTS.append({"url": response.url, "title": title, "text": text, "source": "telangana_pt"})
            print(f"✓ Telangana PT: {title[:50]} — {len(text)} chars")
        for href in response.css("a::attr(href)").getall():
            if not href or any(href.startswith(x) for x in ["javascript:", "#", "mailto:", "tel:"]):
                continue
            if any(href.lower().endswith(x) for x in [".pdf", ".xlsx", ".xls", ".doc", ".zip"]):
                continue
            yield response.follow(href, self.parse)

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(GSTSpider)
    process.crawl(MCASpider)
    process.crawl(ICAISpider)
    process.crawl(CBICSpider)
    process.crawl(EPFSpider)
    process.crawl(ESICSpider)
    process.crawl(TelanganaGSTSpider)
    process.start()


    print(f"\nTotal pages scraped: {len(ALL_RESULTS)}")

    with open("data/gov_pages.json", "w") as f:
        json.dump(ALL_RESULTS, f, indent=2)
    print("Saved to data/gov_pages.json")

    print("Chunking and uploading to Pinecone...")
    all_chunks = []
    for page in ALL_RESULTS:
        chunks = chunk_text(
            text=page["text"],
            source_url=page["url"],
            title=page["title"],
            firm_id="arigato"
        )
        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")
    upsert_chunks(all_chunks)

    stats = get_index().describe_index_stats()
    print(f"Total vectors in Pinecone: {stats['total_vector_count']}")