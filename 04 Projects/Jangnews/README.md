# 🗞 Jang News AI Agent

A professional Python-based autonomous agent that monitors the latest news from Jang (Pakistan) and sends real-time alerts via WhatsApp using the Whapi.cloud API.

## 🚀 Features
- **Real-time Monitoring**: Scrapes the latest news from Jang every 5 minutes (configurable).
- **Intelligent Deduplication**: Uses a local JSON-based database to ensure each news item is only sent once.
- **WhatsApp Integration**: Sends beautifully formatted alerts using the Whapi.cloud API.
- **Robust Logging**: Detailed logging with rotation and retention for long-term monitoring.
- **Production-Ready**: Containerized with Docker for easy 24/7 deployment.

## 📂 Project Structure
```text
.
├── main.py             # Entry point
├── config/             # Configuration management
├── scraper/            # Web scraping logic
├── whatsapp/           # WhatsApp API integration
├── storage/            # Local data storage (database.json)
├── utils/              # Utility functions (logger, summarizer)
├── tests/              # Unit tests and mock data
├── Dockerfile          # Production container setup
└── requirements.txt    # Python dependencies
```

## 🛠 Setup Instructions

### 1. Prerequisites
- Python 3.12+
- A [Whapi.cloud](https://whapi.cloud/) account and API token.

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
WHAPI_API_TOKEN=your_whapi_token_here
WHAPI_RECIPIENT_NUMBER=your_number_with_country_code (e.g. 923001234567)
SCRAPE_INTERVAL_SECONDS=300
```

### 3. Local Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the agent
python main.py
```

## 🐳 Deployment (Run 24/7)

### Option 1: Docker (Recommended)
Docker is the best way to ensure the app runs consistently in the cloud.

1. **Build the image**:
   ```bash
   docker build -t jang-news-agent .
   ```
2. **Run the container**:
   ```bash
   docker run -d \
     --name news-agent \
     --env-file .env \
     -v $(pwd)/storage:/app/storage \
     jang-news-agent
   ```

### Option 2: Cloud Hosting (PaaS)
You can deploy this repository directly to these platforms:
- **[Railway.app](https://railway.app/)**: Connect your GitHub repo, add your `.env` variables, and it will run 24/7 automatically.
- **[Render.com](https://render.com/)**: Choose "Background Worker", connect your repo, and set the environment variables.

### Option 3: VPS (DigitalOcean / AWS / Google Cloud)
1. Install Docker on your VPS.
2. Clone this repository.
3. Run using Docker Compose or the Docker commands above.

## 🛡 License
MIT License
