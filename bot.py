
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

# ====================== ОБРАБОТКА НОВОСТИ ======================

async def process_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = update.message.text.strip()
    source_link = context.user_data.get('source_link', '#')
    original_text = news  # сохраняем оригинал
    
    if contains_scandal_keywords(news):
        translated = translate_scandal(news)
        
        # Сохраняем оригинал для кнопки «Перевести обратно»
        context.user_data['original_text'] = original_text
        
        # Кнопки
        keyboard = [
            [
                InlineKeyboardButton("🔍 Проверить оригинал", url=source_link),
                InlineKeyboardButton("🔄 Перевести обратно", callback_data="show_original")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = f"""
🚨 **СКАНДАЛ / РИСК**

{translated}

⚠️ **Памятка**: Это автоматический перевод. 
Рекомендуется проверять ключевые факты по оригиналу.
        """
        
        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(news)


# ====================== ОБРАБОТКА КНОПКИ ======================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # убираем "часики"
    
    if query.data == "show_original":
        original = context.user_data.get('original_text', 'Оригинал не найден.')
        await query.edit_message_text(
            text=f"**Оригинал (английский):**\n\n{original}",
            parse_mode='Markdown'
        )


# Не забудь добавить handler в main()
# application.add_handler(CallbackQueryHandler(button_handler))
