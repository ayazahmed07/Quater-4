import json
import os
from loguru import logger

class JSONDatabase:
    """
    Simple JSON-based database for persistent storage of processed links.
    Prevents duplicate alerts for the same announcement.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create an empty list in the JSON file if it doesn't exist."""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new database file: {self.file_path}")

    def load_processed_ids(self) -> set:
        """Loads processed announcement IDs into a set for fast lookup."""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return set(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return set()

    def add_id(self, announcement_id: str):
        """Appends a new announcement ID to the database."""
        processed_ids = self.load_processed_ids()
        if announcement_id not in processed_ids:
            processed_ids.add(announcement_id)
            with open(self.file_path, 'w') as f:
                json.dump(list(processed_ids), f, indent=4)
            logger.debug(f"Saved new ID to database: {announcement_id}")

    def is_processed(self, announcement_id: str) -> bool:
        """Checks if an announcement has already been processed."""
        processed_ids = self.load_processed_ids()
        return announcement_id in processed_ids
