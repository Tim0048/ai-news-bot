import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот запущен. Кидай новости!")

async def process_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "CEO" in text or "падение" in text or "обвал" in text or "скандал" in text:
        keyboard = [[InlineKeyboardButton("🔄 Оригинал", callback_data="original")]]
        await update.message.reply_text(f"🚨 Рисковая новость:\n\n{text}", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("Получил сообщение.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Вот оригинал.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_news))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == '__main__':
    main()
