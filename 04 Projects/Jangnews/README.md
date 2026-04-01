# Jang News AI Alert Agent

A professional-level news monitoring and alert system that scrapes the Jang News website for the latest updates and sends real-time alerts via WhatsApp.

## 🚀 Overview

This agent operates as a scheduled workflow that monitors the Jang News "Latest News" category. It identifies new headlines, avoids duplicate notifications using a persistent local database, and pushes formatted alerts to a configured WhatsApp recipient.

## 🛠 Features

- **Automated Scraping**: Periodically checks `jang.com.pk` for new content.
- **Deduplication**: Uses a persistent JSON-based database to ensure each news item is only sent once.
- **WhatsApp Integration**: Sends instant alerts using the Whapi.cloud API.
- **Professional Logging**: Integrated with `loguru` for clean, rotateable logs.
- **Robust Configuration**: Uses `pydantic-settings` for environment variable management and type safety.
- **Dockerized**: Ready for deployment using Docker and Docker Compose.
- **Unit Tested**: Includes basic tests for the scraping logic using `pytest`.

## 📂 Project Structure

```text
├── config/             # Configuration management (pydantic-settings)
├── logs/               # Application logs
├── scraper/            # News scraping logic (BeautifulSoup4)
├── storage/            # Persistent storage (database.json)
├── tests/              # Unit tests
├── whatsapp/           # WhatsApp API integration (Whapi.cloud)
├── main.py             # Entry point
└── Dockerfile          # Containerization setup
```

## ⚙️ Setup & Installation

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   Create a `.env` file based on `.env.example`:
   ```env
   WHAPI_API_TOKEN=your_token_here
   WHAPI_RECIPIENT_NUMBER=your_phone_number
   WHAPI_API_URL=https://gate.whapi.cloud
   ```
4. **Run the Agent**:
   ```bash
   python main.py
   ```

## 🧪 Testing

Run the tests using pytest:
```bash
pytest tests/
```

## 🤖 Agent vs. Workflow

This project is currently a **Robust Workflow**. 

- **Workflow**: It follows a predefined set of instructions (Scrape -> Filter -> Notify). It is reliable, predictable, and efficient for this specific task.
- **Future Agent Potential**: To evolve into a "Full AI Agent," one could integrate an LLM (like GPT-4) to:
  - **Reason** about the importance of news items.
  - **Categorize** news based on user interests.
  - **Summarize** full articles (extending the current snippet logic).
  - **Decide** which notification channel to use based on urgency.
