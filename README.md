# Serverless Telegram Daily Bot 🤖⚡

A fully automated, zero-dependency, serverless daily assistant bot running entirely on **GitHub Actions**. It collects real-time weather data, global news across multiple categories, live sports results, daily tech/philosophy insights, and trending tracks, then dispatches them straight to your Telegram chat.

---

## Architecture & Design 🏛️

* **Serverless & Stateless**: No persistent database or local state files are required. It executes purely on an ephemeral Ubuntu runner provided by GitHub Actions.
* **Zero-Third-Party API Overhead**: Built strictly using Python's standard `urllib` library for network requests, maintaining a lightweight footprint.
* **Automated Media Pipeline**: Integrates `yt-dlp` and `ffmpeg` to download trending audio tracks safely under Telegram's strict file size thresholds.
* **HTML Sanitization Engine**: Dynamically converts Markdown blocks and code snippets into clean Telegram HTML entities for optimal rendering.

---

## Project Structure 📂

```text
telegram_daily_bot/
├── .github/
│   └── workflows/
│       └── daily_report.yml    # Cron schedule & workflow configuration
├── src/
│   ├── __init__.py
│   ├── config.py               # Environment configuration & constants
│   ├── main.py                 # Core orchestration script
│   ├── news.py                 # Multi-category RSS parser
│   ├── song.py                 # Spotify trending fetcher & media downloader
│   ├── sports.py               # Live sports results parser (Soccer/Basketball)
│   ├── telegram_sender.py      # Multipart Telegram API wrapper & HTML sanitizer
│   ├── weather.py              # OpenWeatherMap integration
│   └── writer.py               # Groq LLM integration for smart curation
├── requirements.txt            # Minimal dependency list (yt-dlp)
└── README.md

```

---

## Prerequisites & Environment Variables 🔑

To run this bot successfully, configure the following secrets in your GitHub Repository (`Settings > Secrets and variables > Actions`):

| Secret Name | Description | Required |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot token obtained via [@BotFather](https://t.me/BotFather) | **Yes** |
| `TELEGRAM_USER_ID` | Your personal Telegram Chat ID (fallback target) | **Yes** |
| `TELEGRAM_CHANNEL_ID` | Telegram Channel ID (e.g., `@channel` or `-100xxxx`), leave empty or null to target user chat | No |
| `OPENWEATHER_API_KEY` | API key from [OpenWeatherMap](https://openweathermap.org/) | **Yes** |
| `GROQ_API_KEY` | API key from [Groq Console](https://console.groq.com/) for Llama 3.3 processing | **Yes** |
| `SPOTIFY_CLIENT_ID` | Spotify Developer API Client ID for trending music tracks | No |
| `SPOTIFY_CLIENT_SECRET` | Spotify Developer API Client Secret | No |
| `SPORTRADAR_SOCCER_API_KEY` | Sportradar API key for live soccer updates | No |
| `SPORTRADAR_BASKETBALL_API_KEY` | Sportradar API key for live basketball updates | No |

---

## Workflow Execution (.github/workflows/daily_report.yml) ⚙️

The action is configured to trigger automatically via a cron schedule or manually through the GitHub Actions tab:

```yaml
name: Daily Telegram Report Bot

on:
  schedule:
    - cron: '30 4 * * *' # Executes daily at 04:30 UTC
  workflow_dispatch:

jobs:
  execute-bot:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install System Dependencies (ffmpeg)
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg

      - name: Install Python Requirements
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Main Script
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_USER_ID: ${{ secrets.TELEGRAM_USER_ID }}
          TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}
          OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
          SPOTIFY_CLIENT_ID: ${{ secrets.SPOTIFY_CLIENT_ID }}
          SPOTIFY_CLIENT_SECRET: ${{ secrets.SPOTIFY_CLIENT_SECRET }}
          SPORTRADAR_SOCCER_API_KEY: ${{ secrets.SPORTRADAR_SOCCER_API_KEY }}
        run: python -m src.main

```

---

## Local Setup & Development 🚀

1. **Clone the repository**:
```bash
git clone https://github.com/salman0H/telegram_daily_bot.git
cd telegram_daily_bot

```


2. **Install dependencies**:
```bash
pip install -r requirements.txt

```


3. **Export environment variables**:
```bash
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_USER_ID="your_user_id"
export OPENWEATHER_API_KEY="your_key"
export GROQ_API_KEY="your_key"

```


4. **Run the bot**:
```bash
python -m src.main

```



---

## License 📜

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).
