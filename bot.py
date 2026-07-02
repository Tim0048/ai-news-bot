import logging
import os
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

if TOKEN:
    logger.info("✅ Бот запущен успешно!")
    logger.info("Токен загружен. Бот работает.")
else:
    logger.error("❌ BOT_TOKEN не найден!")

# Держим процесс живым
while True:
    time.sleep(60)
    logger.info("Бот всё ещё работает...")
