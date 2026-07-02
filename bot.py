import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)

# ====================== НАСТРОЙКИ ======================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================== ПЕРЕВОД ======================
# Здесь подключи свой переводчик (Google Translate или другой)
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None
    logger.warning("googletrans не установлен. Перевод будет отключён.")

def translate_text(text: str) -> str:
    if not translator:
        return text
    try:
        return translator.translate(text, dest='ru').text
    except Exception as e:
        logger.error(f"Ошибка перевода: {e}")
        return text

# ====================== ЛОГИКА РИСКОВ ======================
RISK_KEYWORDS = [
    "CEO", "смена CEO", "новый CEO", "retire", "resign", "guidance",
    "прогноз", "earnings miss", "weak outlook", "падает на", "обвал",
    "падение на", "рухнул", "скандал", "расследование", "штраф", "иск"
]

def is_linked_risk_event(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    has_drop = any(word in text_lower for word in ["упал", "падение", "обвал", "drop", "plunge", "fell", "tumble", "рухнул"])
    has_reason = any(kw.lower() in text_lower for kw in RISK_KEYWORDS)
    return has_drop and has_reason


# ====================== ОБРАБОТЧИКИ ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Ждём новости и скандалы.")


async def process_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = update.message.text.strip()
    source_link = context.user_data.get('source_link', '#')
    
    if is_linked_risk_event(news):
        translated = translate_text(news)
        context.user_data['original_text'] = news
        
        keyboard = [
            [InlineKeyboardButton("🔍 Проверить оригинал", url=source_link)],
            [InlineKeyboardButton("🔄 Перевести обратно", callback_data="show_original")]
        ]
        
        message = f"""
🚨 **ПАДЕНИЕ + ПРИЧИНА**

{translated}

⚠️ Это автоматический перевод. 
Рекомендуется проверить ключевые факты по оригиналу.
        """
        
        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        # Можно отключить, если не нужно отвечать на обычные новости
        pass


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "show_original":
        original = context.user_data.get('original_text', 'Оригинал не найден.')
        await query.edit_message_text(
            text=f"**Оригинал:**\n\n{original}",
            parse_mode='Markdown'
        )


# ====================== ЗАПУСК ======================
def main():
    # Вставь сюда свой TOKEN
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_news))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()
