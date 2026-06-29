
import time
import requests
import telebot
import google.generativeai as genai
import os
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

# ====================== ТВОИ КЛЮЧИ ======================
TG_TOKEN = "8799537658:AAEpyC45IAgQFxtIMysMfR0JeKDEN38Xgag"   # ← На 100% точный токен по скриншоту!
GEMINI_KEY = "AQ.Ab8RN6JLCuL6hnLT5XD7_XSA8G2Z8sXZzms6IZErVLv43D5Bbw"
FINNHUB_KEY = "ct90f91r01qhk69v66ogct90f91r01qhk69v66p0"
MY_CHAT_ID = 8560334915

WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "HOOD", "CCL", "SPCX"]

# Инициализация
bot = telebot.TeleBot(TG_TOKEN)
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

processed_news_ids = set()
MAX_PROCESSED = 500


class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"AI Stock Bot is running 24/7 ✅")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), WebServer)
    print(f"🌐 Мини-веб-сервер запущен на порту {port}")
    server.serve_forever()


def get_market_news():
    url = f"https://finnhub.io{FINNHUB_KEY}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка Finnhub: {e}")
        return []


def analyze_with_gemini(headline: str, summary: str) -> str:
    prompt = f"""
Ты опытный financial analyst. 
Проанализируй новость и определи, влияет ли она НАПРЯМУЮ на компании: {', '.join(WATCHLIST)}.
Заголовок: {headline}
Описание: {summary}

Если НЕ влияет — ответь строго одним словом: IGNORE.
Если влияет — дай ответ СТРОГО в формате:
[ТИКЕР] Оценка: [число от -5 до +5]
Краткое объяснение: [1-2 предложения на русском языке]
"""
    try:
        response = ai_model.generate_content(prompt, generation_config={"temperature": 0.3})
        return response.text.strip()
    except Exception as e:
        print(f"❌ Ошибка ИИ: {e}")
        return "IGNORE"


def main_loop():
    print("🚀 ИИ-Бот начинает мониторинг акций...")
    
    initial_news = get_market_news()
    for news in initial_news[:25]:
        if news.get("id"):
            processed_news_ids.add(news.get("id"))
            
    while True:
        news_list = get_market_news()
        for news in news_list[:12]:
            news_id = news.get("id")
            if not news_id or news_id in processed_news_ids:
                continue
                
            headline = news.get("headline", "")
            summary = news.get("summary", "")
            news_url = news.get("url", "")
            
            ai_verdict = analyze_with_gemini(headline, summary)
            
            if "IGNORE" not in ai_verdict:
                emoji = "🟢" if any(f"+{i}" in ai_verdict for i in range(1,6)) else "🔴"
                if "Оценка: 0" in ai_verdict: 
                    emoji = "⚪"
                
                message_text = (
                    f"{emoji} **ИИ-АНАЛИЗ РЫНКА**\n\n"
                    f"📰 **{headline}**\n\n"
                    f"{ai_verdict}\n\n"
                    f"🔗 [Источник]({news_url})"
                )
                try:
                    bot.send_message(MY_CHAT_ID, message_text, parse_mode="Markdown")
                except Exception as e:
                    print(f"❌ Ошибка отправки: {e}")
            
            processed_news_ids.add(news_id)
            
            if len(processed_news_ids) > MAX_PROCESSED:
                processed_news_ids.clear()
                
            time.sleep(1.5)
            
        time.sleep(300)


if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    time.sleep(3)
    
    try:
        bot.send_message(MY_CHAT_ID, "🚀 Проверка связи! Бот успешно запущен на Render.")
    except Exception as e:
        print(f"❌ Ошибка тестовой отправки: {e}")
        
    main_loop()
