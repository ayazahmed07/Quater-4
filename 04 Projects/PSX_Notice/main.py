import time
import sys
from loguru import logger

# Project modules
from config.config import settings
from storage.database import JSONDatabase
from scraper.psx_scraper import JangNewsScraper
from whatsapp.sender import WhatsAppSender

# Configure logging
def setup_logging():
    logger.remove() # Remove default logger
    logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")
    if settings:
        logger.add(settings.log_file, rotation="1 MB", retention="10 days", level="INFO")

def run_agent():
    """
    Main execution loop of the Jang News AI Agent.
    """
    if not settings:
        logger.error("Configuration not loaded. Please ensure .env file is correctly set up.")
        return

    # Initialize components
    db = JSONDatabase(settings.database_file)
    scraper = JangNewsScraper(settings.news_url)
    whatsapp_sender = WhatsAppSender(
        api_url=settings.whapi_api_url,
        api_token=settings.whapi_api_token,
        recipient_number=settings.whapi_recipient_number
    )

    logger.info(f"Jang News Agent started. Monitoring {settings.news_url}...")

    while True:
        try:
            # 1. Fetch current news from Jang
            news_items = scraper.fetch_news()

            if not news_items:
                logger.warning("No news found or failed to fetch. Retrying next cycle.")
            
            for item in news_items:
                news_id = item['id']

                # 2. Check if already processed
                if db.is_processed(news_id):
                    logger.debug(f"News item {news_id} already processed. Skipping.")
                    continue

                logger.info(f"New news detected: {item['title']}")

                # 3. Send alert to WhatsApp
                success = whatsapp_sender.send_alert(item)

                if success:
                    # 4. Save to database to avoid re-processing
                    db.add_id(news_id)
                    logger.success(f"Successfully processed and alerted for {news_id}")
                else:
                    logger.warning(f"Failed to send WhatsApp alert for {news_id}. Will retry in next cycle.")

        except Exception as e:
            logger.critical(f"An unexpected error occurred in the main loop: {e}")
        
        # 5. Sleep until next cycle
        logger.debug(f"Sleeping for {settings.scrape_interval_seconds} seconds...")
        time.sleep(settings.scrape_interval_seconds)

if __name__ == "__main__":
    setup_logging()
    run_agent()
