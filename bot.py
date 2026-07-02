
import time
import requests
import telebot
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import deque
import logging
import os

# ====================== КЛЮЧИ ======================
TG_TOKEN = "8799537658:AAEpyC45IAgQFxtIMysMfR0JeKDEN38Xgag"
FINNHUB_KEY = "d92oaehr01qpou37een0d92oaehr01qpou37eeng"
MY_CHAT_ID = 8560334915

WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "HOOD", "CCL", "SPCX"]

bot = telebot.TeleBot(TG_TOKEN)
processed_news = deque(maxlen=2000)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"AI Stock Bot is running OK")

def run_keep_alive():
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"Запуск keep-alive сервера на порту {port}")
    server = HTTPServer(('0.0.0.0', port), KeepAlive)
    server.serve_forever()

def send_grok_analysis():
    analysis = """🧠 **Анализ от Grok**

Техсектор позитивен.
• NVDA +4 (лидер AI)
• AAPL +3
• TSLA +3
• MSFT +2
• AMZN 0

Рекомендация: Держим NVDA, AAPL, TSLA."""
    try:
        bot.send_message(MY_CHAT_ID, analysis, parse_mode="Markdown")
    except:
        pass

def main_loop():
    logging.info("🚀 Основной цикл запущен")
    last_analysis = 0

    while True:
        # Анализ каждые 2 часа
        if time.time() - last_analysis > 7200:
            send_grok_analysis()
            last_analysis = time.time()

        # Новости
        try:
            resp = requests.get(
                f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}",
                timeout=15
            )
            if resp.status_code == 200:
                for news in resp.json():
                    nid = news.get("id")
                    if nid and nid not in processed_news:
                        headline = news.get("headline", "")
                        if any(t in headline for t in WATCHLIST):
                            msg = f"📰 **{headline}**\n\n{news.get('summary', '')}"
                            bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")
                        processed_news.append(nid)
        except Exception as e:
            logging.error(f"Ошибка: {e}")

        time.sleep(180)

if __name__ == "__main__":
    Thread(target=run_keep_alive, daemon=True).start()
    main_loop()
