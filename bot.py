import logging
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN не найден!")
else:
    logger.info("✅ Бот запущен успешно!")

# Пока бот просто работает и логирует
print("Бот работает...")
