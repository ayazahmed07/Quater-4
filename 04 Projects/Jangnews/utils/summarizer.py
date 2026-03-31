from loguru import logger

class AnnouncementSummarizer:
    """
    Summarizes the extracted text from PSX announcement PDFs.
    Uses simple rule-based logic to provide a short snippet.
    """
    def summarize(self, text: str, max_length: int = 300) -> str:
        """
        Creates a short summary from the full extracted text.
        In a production environment, this could be replaced with an AI-based summarizer (e.g., GPT-4).
        """
        if not text:
            return "No content could be extracted from the PDF."

        # Take the first few lines or characters
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Simple heuristic: often the first few lines of an announcement 
        # contain the most important information (e.g., "Board Meeting Result", "Quarterly Report").
        summary = " ".join(lines[:10]) # Get first 10 lines
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
            
        logger.debug(f"Generated summary of length {len(summary)}")
        return summary
