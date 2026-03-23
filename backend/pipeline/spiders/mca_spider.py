import scrapy
from scrapy.crawler import CrawlerProcess

RESULTS = []

class MCASpider(scrapy.Spider):
    name = "mca"
    start_urls = [
        "https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/acts.html",
        "https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks/rules.html",
    ]
    allowed_domains = ["mca.gov.in"]

    custom_settings = {
        "DEPTH_LIMIT": 2,
        "DOWNLOAD_DELAY": 2,
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "WARNING",
        "HTTPERROR_ALLOW_ALL": True,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    }

    def parse(self, response):
        content_type = response.headers.get("Content-Type", b"").decode().lower()
        if "text/html" not in content_type:
            return

        print(f"Visiting: {response.url} — status: {response.status}")

        title = response.css("title::text").get(default="").strip()
        content = response.css(
            "p::text, h1::text, h2::text, h3::text, h4::text, li::text, td::text, span::text"
        ).getall()
        text = " ".join(c.strip() for c in content if c.strip())

        if len(text) > 200:
            RESULTS.append({
                "url": response.url,
                "title": title,
                "text": text
            })
            print(f"✓ Scraped: {title[:60]} — {len(text)} chars")

        for href in response.css("a::attr(href)").getall():
            if not href:
                continue
            if any(href.startswith(x) for x in [
                "javascript:", "#", "mailto:", "tel:", "void", "data:"
            ]):
                continue
            if any(href.lower().endswith(x) for x in [
                ".pdf", ".xlsx", ".xls", ".doc", ".docx", ".zip", ".png", ".jpg"
            ]):
                continue
            yield response.follow(href, self.parse)


def run_mca_spider() -> list[dict]:
    global RESULTS
    RESULTS = []
    process = CrawlerProcess()
    process.crawl(MCASpider)
    process.start()
    return RESULTS