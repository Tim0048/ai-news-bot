RISK_KEYWORDS = [
    "CEO", "смена CEO", "новый CEO", "retire", "resign", "guidance", 
    "прогноз", "earnings miss", "weak outlook", "падает на", "обвал", 
    "падение на", "рухнул", "скандал", "расследование"
]

def is_linked_risk_event(text: str) -> bool:
    text_lower = text.lower()
    has_drop = any(word in text_lower for word in ["упал", "падение", "обвал", "drop", "plunge", "fell", "tumble"])
    has_reason = any(kw in text_lower for kw in RISK_KEYWORDS)
    return has_drop and has_reason


async def process_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    news = update.message.text.strip()
    source_link = context.user_data.get('source_link')
    
    if is_linked_risk_event(news):
        translated = translate_scandal(news)
        context.user_data['original_text'] = news
        
        keyboard = [
            [InlineKeyboardButton("🔍 Проверить оригинал", url=source_link)],
            [InlineKeyboardButton("🔄 Перевести обратно", callback_data="show_original")]
        ]
        
        message = f"""
🚨 **ПАДЕНИЕ + ПРИЧИНА**

{translated}

⚠️ Автоперевод. Рекомендуется проверить оригинал.
        """
        
        await update.message.reply_text(
            message, 
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
