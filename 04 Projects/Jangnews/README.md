# PSX AI Agent 📢

A 24/7 automation system that monitors the Pakistan Stock Exchange (PSX) notifications page, extracts PDF content, and sends real-time alerts to WhatsApp.

## 🚀 Features
- **Real-time Monitoring**: Scrapes PSX notifications every 5 minutes.
- **Smart Duplicate Prevention**: Uses a local JSON database to avoid sending the same alert twice.
- **PDF Text Extraction**: Downloads and extracts text from announcement PDFs.
- **Intelligent Alerts**: Sends formatted WhatsApp messages via Twilio.
- **Robust Logging**: Keeps track of all activities and errors.

## 📁 Project Structure
```
psx-ai-agent/
├── main.py            # Main entry point and orchestration loop
├── scraper/           # Logic for scraping PSX website
├── pdf/               # Logic for PDF downloading and text extraction
├── whatsapp/          # Twilio WhatsApp API integration
├── storage/           # Persistent storage for processed IDs (JSON database)
├── config/            # Environment variable configuration
├── utils/             # Helper utilities (Summarizer, Logger)
├── logs/              # Log files for debugging and monitoring
└── requirements.txt   # Python dependencies
```

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- A Twilio account (Sign up at [twilio.com](https://www.twilio.com/))
- Twilio WhatsApp Sandbox configured

### 2. Installation
Clone the repository and install the required dependencies:
```bash
# Clone the project (if applicable)
# git clone <repo_url>
# cd psx-ai-agent

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy the `.env.example` file to a new file named `.env` and fill in your details:
```bash
cp .env.example .env
```
Edit the `.env` file with your Twilio credentials:
- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID.
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token.
- `TWILIO_WHATSAPP_FROM`: Your Twilio WhatsApp Sandbox number (e.g., `whatsapp:+14155238886`).
- `TWILIO_WHATSAPP_TO`: Your personal WhatsApp number (e.g., `whatsapp:+92XXXXXXXXXX`).

### 4. Running the Agent
Start the agent by running:
```bash
python main.py
```

## 📝 How it Works
1. **Scrape**: The `PSXScraper` fetches the announcements from the PSX website.
2. **Filter**: It checks against `storage/database.json` to see if the announcement is new.
3. **Process**: If new, it downloads the PDF and extracts text using `pdfplumber`.
4. **Summarize**: A simple rule-based summarizer extracts the most important lines.
5. **Alert**: The `WhatsAppSender` sends a professional message to your phone.
6. **Log**: Every step is recorded in `logs/psx_agent.log`.

## ⚠️ Important Note
The PSX website may have anti-scraping measures. This tool uses standard headers to mimic a browser, but for production use, consider using a rotating proxy or a headless browser if you face blocks.

## 🤝 Contributing
Feel free to fork this project and add features like OpenAI-based summarization or support for multiple notification channels!
