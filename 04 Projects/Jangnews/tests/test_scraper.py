import pytest
import responses
from scraper.jang_scraper import JangNewsScraper

@responses.activate
def test_fetch_news_success():
    """
    Test that fetch_news successfully parses a mock response.
    """
    mock_url = "https://jang.com.pk/category/latest-news"
    mock_html = """
    <html>
        <body>
            <a href="https://jang.com.pk/news/12345-title-one">
                <h2>Headline One</h2>
            </a>
            <a href="https://jang.com.pk/news/67890-title-two">
                <h2>Headline Two</h2>
            </a>
        </body>
    </html>
    """
    
    responses.add(responses.GET, mock_url, body=mock_html, status=200)
    
    scraper = JangNewsScraper(mock_url)
    news = scraper.fetch_news()
    
    assert len(news) == 2
    assert news[0]['title'] == "Headline One"
    assert news[0]['id'] == "12345-title-one"
    assert news[1]['id'] == "67890-title-two"

def test_fetch_news_failure():
    """
    Test that fetch_news handles request failure gracefully.
    """
    mock_url = "https://jang.com.pk/category/latest-news"
    responses.add(responses.GET, mock_url, status=500)
    
    scraper = JangNewsScraper(mock_url)
    news = scraper.fetch_news()
    
    assert news == []
