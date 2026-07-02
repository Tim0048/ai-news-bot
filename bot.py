import time
import requests
import telebot
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import deque
import logging
import os

TG_TOKEN = "8799537658:AAEpyC45IAgQFxtIMysMfR0JeKDEN38Xgag"
FINNHUB_KEY = "d92oaehr01qpou37een0d92oaehr01qpou37eeng"
MY_CHAT_ID = 8560334915

WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "HOOD", "CCL", "SPCX"]

bot = telebot.TeleBot(TG_TOKEN)
processed_news = deque(maxlen=4000)

logging.basicConfig(level=logging.INFO)

SCANDAL_WORDS = ["scandal", "investigation", "lawsuit", "fine", "fraud", "SEC", "probe", "controversy", "resign", "fired", "recall", "ban", "crisis", "allegation"]

class KeepAlive(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_keep_alive():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), KeepAlive).serve_forever()

def is_scandal(headline, summary):
    text = (headline + " " + summary).lower()
    return any(word in text for word in SCANDAL_WORDS)

def send_grok_analysis():
    analysis = """🧠 **Анализ рынка от Grok**

Техсектор сейчас в позитивном настроении.

• NVDA +4 (лидер AI)
• AAPL +3
• TSLA +3
• MSFT +2
• AMZN 0

Рекомендация: Основные позиции держать в NVDA, AAPL и TSLA."""
    bot.send_message(MY_CHAT_ID, analysis, parse_mode="Markdown")

def main_loop():
    logging.info("🚀 Бот запущен")
    last_analysis = 0

    while True:
        if time.time() - last_analysis > 7200:  # каждые 2 часа
            send_grok_analysis()
            last_analysis = time.time()

        try:
            data = requests.get(f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}", timeout=15).json()
            for news in data:
                nid = news.get("id")
                if nid and nid not in processed_news:
                    headline = news.get("headline", "")
                    summary = news.get("summary", "")
                    url = news.get("url", "")

                    if is_scandal(headline, summary):
                        msg = f"🚨 **СКАНДАЛ / РИСК**\n\n{headline}\n\n{summary}\n\n🔗 [Источник]({url})"
                        bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")
                    elif any(t in headline for t in WATCHLIST):
                        msg = f"📰 **{headline}**\n\n{summary}\n\n🔗 [Источник]({url})"
                        bot.send_message(MY_CHAT_ID, msg, parse_mode="Markdown")

                    processed_news.append(nid)
        except:
            pass

        time.sleep(180)

if __name__ == "__main__":
    Thread(target=run_keep_alive, daemon=True).start()
    main_loop()
