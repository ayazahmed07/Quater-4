import requests
from loguru import logger
from typing import Dict, Optional

class WhatsAppSender:
    """
    Sends WhatsApp alerts using the Whapi.cloud API.
    """
    def __init__(self, api_url: str, api_token: str, recipient_number: str):
        self.api_url = api_url.rstrip('/')
        self.api_token = api_token
        self.recipient_number = recipient_number

    def send_alert(self, news_item: Dict, summary: Optional[str] = None) -> bool:
        """
        Sends a formatted news alert via Whapi.cloud.
        """
        message_body = (
            f"🗞 *Jang Latest News*\n\n"
            f"{news_item.get('title', 'N/A')}\n\n"
        )
        
        if summary:
            message_body += f"*Summary:*\n{summary}\n\n"
            
        message_body += f"*Link:*\n{news_item.get('url', 'N/A')}"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }

        payload = {
            "to": self.recipient_number,
            "body": message_body
        }

        try:
            logger.info(f"Sending news alert: {news_item.get('title')[:30]}... to {self.recipient_number}")
            response = requests.post(f"{self.api_url}/messages/text", json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.success(f"Successfully sent news alert via Whapi.cloud")
                return True
            else:
                logger.error(f"Whapi API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send news alert: {e}")
            return False
