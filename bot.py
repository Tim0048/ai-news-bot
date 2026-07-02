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

def translate_text(text: str) -> str:
    return text

RISK_KEYWORDS = [
    "CEO", "смена CEO", "новый CEO", "retire", "resign", "guidance",
    "прогноз", "earnings miss", "weak outlook", "падает на", "обвал",
    "падение на", "рухнул", "скандал"
]

def is_linked_risk_event(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    has_drop = any(w in text_lower for w in ["упал", "падение", "обвал", "drop", "plunge", "fell", "tumble", "рухнул"])
    has_reason = any(kw in text_lower for kw in RISK_KEYWORDS)
    return has_drop and has_reason


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен. Ждём скандалы и падения акций.")


async def process_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = update.message.text.strip()
    if is_linked_risk_event(news):
        keyboard = [[InlineKeyboardButton("🔄 Показать оригинал", callback_data="show_original")]]
        await update.message.reply_text(
            f"🚨 **РИСКОВАЯ НОВОСТЬ**\n\n{news}",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "show_original":
        await query.edit_message_text(f"**Оригинал:**\n\n{query.message.text}")


def main():
    TOKEN = "ТОКЕН_СЮДА"   # ← Замени на свой токен от @BotFather
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_news))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
