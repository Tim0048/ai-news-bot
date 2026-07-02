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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Простая заглушка для перевода (можно потом заменить на нормальный)
def translate_text(text: str) -> str:
    return text  # Пока возвращаем оригинал, чтобы бот не падал

# ====================== ЛОГИКА ======================
RISK_KEYWORDS = [
    "CEO", "смена CEO", "новый CEO", "retire", "resign", "guidance",
    "прогноз", "earnings miss", "weak outlook", "падает на", "обвал",
    "падение на", "рухнул", "скандал", "расследование"
]

def is_linked_risk_event(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    has_drop = any(w in text_lower for w in ["упал", "падение", "обвал", "drop", "plunge", "fell", "tumble", "рухнул"])
    has_reason = any(kw in text_lower for kw in RISK_KEYWORDS)
    return has_drop and has_reason


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен и готов ловить падения и скандалы.")


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

⚠️ Автоперевод. Проверь оригинал.
        """
        await update.message.reply_text(message, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "show_original":
        original = context.user_data.get('original_text', 'Оригинал не найден.')
        await query.edit_message_text(f"**Оригинал:**\n\n{original}", parse_mode='Markdown')


def main():
    TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_news))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
