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

# ====================== ТВОИ КЛЮЧИ ======================
TG_TOKEN = "8799537658:AAEpyC45IAgQFxtIMysMfR0JeKDEN38Xgag"
GEMINI_KEY = "AQ.Ab8RN6JLCuL6hnLT5XD7_XSA8G2Z8sXZzms6IZErVLv43D5Bbw"
FINNHUB_KEY = "ct90f91r01qhk69v66ogct90f91r01qhk69v66p0"
MY_CHAT_ID = 8560334915

WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "HOOD", "CCL", "SPCX"]

# Настройки
CHECK_INTERVAL = 180          # секунд (3 минуты)
MAX_NEWS_AGE_HOURS = 2        # игнорировать новости старше
DAILY_REPORT_HOUR = 8         # час ежедневного отчёта (по МСК)

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)

# Инициализация
bot = telebot.TeleBot(TG_TOKEN)
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

processed_news = deque(maxlen=3000)
last_min_id = 0
last_daily_report = None


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


def is_news_too_old(news):
    try:
        dt = datetime.fromtimestamp(news.get("datetime", 0))
        return datetime.now() - dt > timedelta(hours=MAX_NEWS_AGE_HOURS)
    except:
        return False


def get_market_news(min_id: int = 0):
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}&minId={min_id}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Finnhub error: {e}")
        return []


def analyze_with_gemini(headline: str, summary: str) -> str:
    prompt = f"""
Ты опытный финансовый аналитик. Проанализируй влияние новости на компании: {', '.join(WATCHLIST)}.

Заголовок: {headline}
Описание: {summary}

Ответь **строго** по правилам:
- Если прямого влияния нет → IGNORE
- Если есть влияние → 
[ТИКЕР] Оценка: [от -5 до +5]
Краткое объяснение: [1-2 предложения на русском]
"""
    try:
        response = ai_model.generate_content(
            prompt,
            generation_config={"temperature": 0.25, "max_output_tokens": 400}
        )
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return "IGNORE"


def send_daily_report():
    global last_daily_report
    now = datetime.now()
    
    if last_daily_report and (now - last_daily_report).days < 1:
        return
    
    if now.hour == DAILY_REPORT_HOUR:
        try:
            message = (
                "🌅 **Ежедневный отчёт ИИ-Бота**\n\n"
                f"📊 Мониторим: {', '.join(WATCHLIST)}\n"
                f"🕒 Время: {now.strftime('%d.%m.%Y %H:%M')}\n\n"
                "Бот работает в штатном режиме."
            )
            bot.send_message(MY_CHAT_ID, message, parse_mode="Markdown")
            last_daily_report = now
            logging.info("Ежедневный отчёт отправлен")
        except Exception as e:
            logging.error(f"Ошибка ежедневного отчёта: {e}")


def main_loop():
    global last_min_id
    logging.info("🚀 ИИ-Бот запущен и готов к работе")

    while True:
        try:
            send_daily_report()
            
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

                ai_verdict = analyze_with_gemini(headline, summary)

                if "IGNORE" not in ai_verdict.upper():
                    if any(f"+{i}" in ai_verdict for i in range(1, 6)):
                        emoji = "🟢"
                    elif any(f"-{i}" in ai_verdict for i in range(1, 6)):
                        emoji = "🔴"
                    else:
                        emoji = "⚪"

                    message_text = (
                        f"{emoji} **ИИ-АНАЛИЗ РЫНКА**\n\n"
                        f"📰 **{headline}**\n\n"
                        f"{ai_verdict}\n\n"
                        f"🔗 [Источник]({news_url})"
                    )

                    bot.send_message(MY_CHAT_ID, message_text, parse_mode="Markdown")
                    logging.info(f"Отправлен сигнал: {headline[:60]}...")

                processed_news.append(news_id)
                last_min_id = max(last_min_id, news_id)

        except Exception as e:
            logging.error(f"Ошибка в главном цикле: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    main_loop()
