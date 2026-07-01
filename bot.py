import time
import requests
import telebot
import google.generativeai as genai
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import deque
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# ====================== КЛЮЧИ ======================
TG_TOKEN = os.getenv("TG_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")
FINNHUB_KEY = os.getenv("FINNHUB_KEY")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID"))

if not all([TG_TOKEN, GEMINI_KEY, FINNHUB_KEY, MY_CHAT_ID]):
    raise SystemExit("❌ Ошибка: Не все ключи найдены в .env файле!")

WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "HOOD", "CCL", "SPCX"]

CHECK_INTERVAL = 180
MAX_NEWS_AGE_HOURS = 2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

bot = telebot.TeleBot(TG_TOKEN)

# Инициализация Gemini
try:
    genai.configure(api_key=GEMINI_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
    logging.info("✅ Gemini успешно инициализирован")
except Exception as e:
    logging.error(f"Gemini init error: {e}")
    ai_model = None


class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"AI Stock Bot is running 24/7 OK")


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    logging.info(f"🌐 Веб-сервер запущен на порту {port}")
    server.serve_forever()


def get_market_news(min_id: int = 0):
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}&minId={min_id}"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Finnhub error: {e}")
        return []


def is_news_too_old(news):
    try:
        dt = datetime.fromtimestamp(news.get("datetime", 0))
        return datetime.now() - dt > timedelta(hours=MAX_NEWS_AGE_HOURS)
    except:
        return False


def analyze_with_gemini(headline: str, summary: str) -> str:
    if not ai_model:
        return "IGNORE"
    prompt = f"""
Ты опытный финансовый аналитик.
Проанализируй новость на влияние на компании: {', '.join(WATCHLIST)}.

Заголовок: {headline}
Описание: {summary}

Если не влияет напрямую — ответь только словом IGNORE.
Если влияет — ответь в формате:
[ТИКЕР] Оценка: [число]
Краткое объяснение: ...
"""
    try:
        response = ai_model.generate_content(prompt, generation_config={"temperature": 0.3})
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return "IGNORE"


def main_loop():
    global last_min_id
    logging.info("🚀 ИИ-Бот запущен")

    while True:
        try:
            news_list = get_market_news(last_min_id)
            for news in news_list:
                news_id = news.get("id")
                if not news_id or news_id in processed_news:
                    continue
                if is_news_too_old(news):
                    continue

                headline = news.get("headline", "")
                summary = news.get("summary", "")
                news_url = news.get("url", "")

                verdict = analyze_with_gemini(headline, summary)

                if "IGNORE" not in verdict.upper():
                    emoji = "🟢" if "+" in verdict else "🔴"
                    msg = f"{emoji} **ИИ-АНАЛИЗ РЫНКА**\n\n📰 {headline}\n\n{verdict}\n\n🔗 [Источник]({news_url})"
                    bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")
                    logging.info(f"Сигнал отправлен: {headline[:60]}...")

                processed_news.append(news_id)
                last_min_id = max(last_min_id, news_id)

        except Exception as e:
            logging.error(f"Ошибка в цикле: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    main_loop()
