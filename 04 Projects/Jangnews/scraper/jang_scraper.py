import requests
from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict

class JangNewsScraper:
    """
    Scrapes the Jang News page for latest news headlines and links.
    """
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_news(self) -> List[Dict]:
        """
        Fetches and parses the Jang News page.
        Returns a list of dictionaries containing news details.
        """
        try:
            logger.debug(f"Fetching news from {self.url}")
            response = requests.get(self.url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []

            # Based on manual analysis, news items are in <a> tags containing <h2>
            items = soup.select('a:has(h2)')

            for item in items:
                try:
                    title = item.find('h2').text.strip()
                    link = item['href']
                    
                    if not link.startswith('http'):
                        from urllib.parse import urljoin
                        link = urljoin(self.url, link)

                    # Unique ID based on the link or title hash
                    news_id = link.rstrip('/').split('/')[-1]

                    news_items.append({
                        'id': news_id,
                        'title': title,
                        'url': link
                    })
                except Exception as e:
                    logger.error(f"Error parsing news item: {e}")
                    continue

            logger.info(f"Found {len(news_items)} news items on the page.")
            return news_items

        except requests.RequestException as e:
            logger.error(f"Failed to fetch news: {e}")
            return []
