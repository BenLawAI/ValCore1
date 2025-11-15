"""
Bestseller Scraper - Scrapes bestseller lists from Amazon, NYT, USA Today
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import random
from loguru import logger
from playwright.sync_api import sync_playwright, Page, Browser
from bs4 import BeautifulSoup


class BestsellerScraper:
    """Scrapes bestseller lists from multiple sources"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self, headless: bool = True):
        """Initialize scraper

        Args:
            headless: Run browser in headless mode
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context = None

    def _random_delay(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """Random delay to avoid detection"""
        time.sleep(random.uniform(min_sec, max_sec))

    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.USER_AGENTS)

    def start(self):
        """Start browser session"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(user_agent=self._get_random_user_agent())
        logger.info("Browser session started")

    def stop(self):
        """Stop browser session"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser session stopped")

    def scrape_amazon(self, genre: str = "overall") -> List[Dict[str, Any]]:
        """Scrape Amazon bestsellers

        Args:
            genre: Genre to scrape (overall, thriller, etc.)

        Returns:
            List of {rank, title, author} dicts
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")

        # Amazon bestseller URLs
        urls = {
            "overall": "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books/",
            "thriller": "https://www.amazon.com/Best-Sellers-Books-Thrillers/zgbs/books/16190/",
            "fantasy": "https://www.amazon.com/Best-Sellers-Books-Fantasy/zgbs/books/16190/",
            "scifi": "https://www.amazon.com/Best-Sellers-Books-Science-Fiction/zgbs/books/16272/",
        }

        url = urls.get(genre, urls["overall"])

        page = self.context.new_page()

        try:
            logger.info(f"Scraping Amazon {genre} bestsellers...")
            page.goto(url, timeout=30000, wait_until="networkidle")

            self._random_delay()

            # Get page content
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            bestsellers = []

            # Amazon uses specific selectors for bestseller items
            items = soup.select("div[id^='gridItemRoot']")

            for idx, item in enumerate(items[:20], start=1):  # Top 20
                try:
                    # Title
                    title_elem = item.select_one("div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
                    title = title_elem.get_text(strip=True) if title_elem else "Unknown"

                    # Author (may not always be present)
                    author_elem = item.select_one("a.a-size-base")
                    author = author_elem.get_text(strip=True) if author_elem else "Unknown"

                    bestsellers.append(
                        {
                            "rank": idx,
                            "title": title,
                            "author": author,
                            "source": "amazon",
                            "genre": genre,
                            "scraped_at": datetime.utcnow(),
                        }
                    )

                    logger.debug(f"  {idx}. {title} by {author}")

                except Exception as e:
                    logger.warning(f"Failed to parse item {idx}: {e}")
                    continue

            logger.info(f"Scraped {len(bestsellers)} Amazon bestsellers")
            return bestsellers

        except Exception as e:
            logger.error(f"Amazon scraping failed: {e}")
            return []

        finally:
            page.close()

    def scrape_nyt(self, list_name: str = "combined-print-and-e-book-fiction") -> List[Dict[str, Any]]:
        """Scrape NYT bestsellers

        Args:
            list_name: NYT list name

        Returns:
            List of {rank, title, author} dicts
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")

        url = f"https://www.nytimes.com/books/best-sellers/{list_name}/"

        page = self.context.new_page()

        try:
            logger.info(f"Scraping NYT {list_name} bestsellers...")
            page.goto(url, timeout=30000, wait_until="networkidle")

            self._random_delay()

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            bestsellers = []

            # NYT uses specific structure for bestseller items
            # Note: NYT structure changes frequently, this is a best-effort parser
            items = soup.select("li[class*='css-']")

            rank = 1
            for item in items[:20]:  # Top 20
                try:
                    # Try to find title and author
                    title_elem = item.select_one("h3")
                    author_elem = item.select_one("p[class*='author']")

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    author = author_elem.get_text(strip=True).replace("by ", "") if author_elem else "Unknown"

                    bestsellers.append(
                        {
                            "rank": rank,
                            "title": title,
                            "author": author,
                            "source": "nyt",
                            "genre": list_name,
                            "scraped_at": datetime.utcnow(),
                        }
                    )

                    logger.debug(f"  {rank}. {title} by {author}")
                    rank += 1

                except Exception as e:
                    logger.warning(f"Failed to parse NYT item: {e}")
                    continue

            logger.info(f"Scraped {len(bestsellers)} NYT bestsellers")
            return bestsellers

        except Exception as e:
            logger.error(f"NYT scraping failed: {e}")
            return []

        finally:
            page.close()

    def scrape_usatoday(self) -> List[Dict[str, Any]]:
        """Scrape USA Today bestsellers

        Returns:
            List of {rank, title, author} dicts
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")

        url = "https://www.usatoday.com/entertainment/books/best-selling/"

        page = self.context.new_page()

        try:
            logger.info("Scraping USA Today bestsellers...")
            page.goto(url, timeout=30000, wait_until="networkidle")

            self._random_delay()

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            bestsellers = []

            # USA Today structure
            items = soup.select("div.book-list-item")

            for idx, item in enumerate(items[:20], start=1):
                try:
                    title_elem = item.select_one(".book-title")
                    author_elem = item.select_one(".book-author")

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    author = author_elem.get_text(strip=True).replace("by ", "") if author_elem else "Unknown"

                    bestsellers.append(
                        {
                            "rank": idx,
                            "title": title,
                            "author": author,
                            "source": "usatoday",
                            "genre": "overall",
                            "scraped_at": datetime.utcnow(),
                        }
                    )

                    logger.debug(f"  {idx}. {title} by {author}")

                except Exception as e:
                    logger.warning(f"Failed to parse USA Today item: {e}")
                    continue

            logger.info(f"Scraped {len(bestsellers)} USA Today bestsellers")
            return bestsellers

        except Exception as e:
            logger.error(f"USA Today scraping failed: {e}")
            return []

        finally:
            page.close()

    def scrape_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape all sources

        Returns:
            Dict of {source: bestseller_list}
        """
        results = {}

        # Amazon
        try:
            results["amazon_overall"] = self.scrape_amazon("overall")
        except Exception as e:
            logger.error(f"Amazon scraping failed: {e}")
            results["amazon_overall"] = []

        self._random_delay()

        # NYT
        try:
            results["nyt_fiction"] = self.scrape_nyt("combined-print-and-e-book-fiction")
        except Exception as e:
            logger.error(f"NYT scraping failed: {e}")
            results["nyt_fiction"] = []

        self._random_delay()

        # USA Today
        try:
            results["usatoday"] = self.scrape_usatoday()
        except Exception as e:
            logger.error(f"USA Today scraping failed: {e}")
            results["usatoday"] = []

        return results


# Example usage
if __name__ == "__main__":
    scraper = BestsellerScraper(headless=True)
    scraper.start()

    try:
        results = scraper.scrape_all()

        for source, books in results.items():
            print(f"\n{source.upper()}: {len(books)} books")
            for book in books[:5]:
                print(f"  {book['rank']}. {book['title']} by {book['author']}")

    finally:
        scraper.stop()
