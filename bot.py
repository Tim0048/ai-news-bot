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
processed_news = deque(maxlen=2000)

logging.basicConfig(level=logging.INFO)

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"AI Stock Bot is running OK")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"Starting web server on port {port}")
    server = HTTPServer(('0.0.0.0', port), WebServer)
    server.serve_forever()

def get_market_news():
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def main_loop():
    logging.info("🚀 Бот запущен")
    while True:
        news_list = get_market_news()
        for news in news_list:
            nid = news.get("id")
            if nid and nid not in processed_news:
                headline = news.get("headline", "")
                if any(t in headline for t in WATCHLIST):
                    msg = f"📰 {headline}\n\n{news.get('summary','')}"
                    bot.send_message(MY_CHAT_ID, msg)
                processed_news.append(nid)
        time.sleep(180)

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    main_loop()
