import time
import requests
import telebot
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import deque
import logging

TG_TOKEN = "8799537658:AAEpyC45IAgQFxtIMysMfR0JeKDEN38Xgag"
FINNHUB_KEY = "d92oaehr01qpou37een0d92oaehr01qpou37eeng"
MY_CHAT_ID = 8560334915

WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "HOOD", "CCL", "SPCX"]

bot = telebot.TeleBot(TG_TOKEN)
processed_news = deque(maxlen=2000)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), WebServer).serve_forever()

def get_market_news():
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def send_grok_analysis():
    analysis = """🧠 **Анализ от Grok**

**Текущий фон:** Позитивный для AI и техсектора.

**NVDA** — +4 (лидер)
**AAPL** — +3
**TSLA** — +3
**MSFT** — +2
**AMZN** — 0

Рекомендация: Держим основные позиции в NVDA, AAPL, TSLA."""
    try:
        bot.send_message(MY_CHAT_ID, analysis, parse_mode="Markdown")
    except:
        pass

def main_loop():
    logging.info("🚀 Бот запущен")
    last_analysis_time = 0

    while True:
        # Отправляем анализ раз в час
        if time.time() - last_analysis_time > 3600:
            send_grok_analysis()
            last_analysis_time = time.time()

        # Проверяем новости
        news_list = get_market_news()
        for news in news_list:
            news_id = news.get("id")
            if not news_id or news_id in processed_news:
                continue

            headline = news.get("headline", "")
            summary = news.get("summary", "")
            url = news.get("url", "")

            if any(ticker in headline.upper() or ticker in summary.upper() for ticker in WATCHLIST):
                msg = f"📰 **{headline}**\n\n{summary}\n\n🔗 [Источник]({url})"
                try:
                    bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")
                    logging.info("Новость отправлена")
                except:
                    pass

            processed_news.append(news_id)

        time.sleep(180)

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    main_loop()
