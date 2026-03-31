import requests
import pdfplumber
import os
from loguru import logger
from typing import Optional

class PDFProcessor:
    """
    Handles downloading and extracting text from PDF files.
    """
    def __init__(self, download_dir: str = 'temp_pdfs'):
        self.download_dir = download_dir
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        """Create a temporary directory for downloading PDFs."""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            logger.info(f"Created temporary PDF download directory: {self.download_dir}")

    def download_pdf(self, pdf_url: str, filename: str) -> Optional[str]:
        """Downloads the PDF to a temporary file and returns its path."""
        try:
            logger.debug(f"Downloading PDF from {pdf_url}")
            filepath = os.path.join(self.download_dir, filename)
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.debug(f"Successfully downloaded PDF to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            return None

    def extract_text(self, filepath: str) -> str:
        """Extracts text from the PDF file using pdfplumber."""
        try:
            logger.debug(f"Extracting text from PDF: {filepath}")
            all_text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
            
            # Clean up the text by stripping extra whitespace
            return all_text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {filepath}: {e}")
            return ""
        finally:
            # Optionally remove the PDF file after extraction
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    logger.warning(f"Could not delete temporary PDF file {filepath}: {e}")
