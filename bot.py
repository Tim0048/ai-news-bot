import logging
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv("BOT_TOKEN"):
    logger.info("✅ Бот запущен успешно!")
else:
    logger.error("❌ Токен не найден!")

print("Бот работает...")

# Чтобы процесс не завершался
while True:
    time.sleep(300)  # каждые 5 минут пишет в лог
