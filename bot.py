import time
import requests
import telebot
import google.generativeai as genai
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# === ВАШИ КЛЮЧИ ===
TG_TOKEN = "8799537658:AAEpyC45IAgQFXtIMysMfr0JeKDEN38Xgag"
GEMINI_KEY = "AQ.Ab8RN6JLCuL6hnLT5XD7_XSA8G2Z8sXZzms6IZErVLv43D5Bbw"
MY_CHAT_ID = "8560334915"
FINNHUB_KEY = "ct90f91r01qhk69v66ogct90f91r01qhk69v66p0"
WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"]

bot = telebot.TeleBot(TG_TOKEN)
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
processed_news_ids = set()

# Мини веб-сервер для обхода ограничений Render
# Живой веб-сервер, чтобы Render не закрывал бесплатный сервис
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"AI Bot is working 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), WebServer)
    server.serve_forever()

def get_market_news():
    url = f"https://finnhub.io{FINNHUB_KEY}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200: return response.json()
    except: pass
    return []

def analyze_with_gemini(headline, summary):
    prompt = f"Ты финансовый аналитик. Определи, влияет ли новость НАПРЯМУЮ на {', '.join(WATCHLIST)}. Заголовок: {headline}. Описание: {summary}. Если НЕ влияет, ответь СТРОГО одним словом IGNORE. Если влияет, дай ответ в формате: [ТИКЕР] Оценка: [от -5 до +5]. Краткое объяснение на русском языке."
    try:
        response = ai_model.generate_content(prompt)
        return response.text.strip()
    except: return "IGNORE"

def main_loop():
    initial_news = get_market_news()
    for news in initial_news[:20]:
        if news.get("id"): processed_news_ids.add(news.get("id"))
            
    while True:
        news_list = get_market_news()
        for news in news_list[:10]:
            news_id = news.get("id")
            if news_id in processed_news_ids: continue
                
            headline = news.get("headline", "")
            summary = news.get("summary", "")
            news_url = news.get("url", "")
            
            ai_verdict = analyze_with_gemini(headline, summary)
            if "IGNORE" not in ai_verdict:
                emoji = "🟢" if "Оценка: +" in ai_verdict or any(f"Оценка: {i}" for i in range(1, 6)) else "🔴"
                if "Оценка: 0" in ai_verdict: emoji = "⚪"
                
                message_text = f"{emoji} **ИИ-АНАЛИЗ РЫНКА**\n\n" f"📰 **{headline}**\n\n" f"{ai_verdict}\n\n" f"🔗 [Источник]({news_url})"
                try: bot.send_message(MY_CHAT_ID, message_text, parse_mode="Markdown")
                except: pass
            processed_news_ids.add(news_id)
            time.sleep(2)
        time.sleep(300)

if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()

    # ТЕСТОВАЯ СТРОКА ДЛЯ ПРОВЕРКИ СВЯЗИ:
    bot.send_message(MY_CHAT_ID, "🚀 Проверка")

    main_loop()

