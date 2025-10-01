import os
import logging
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text("🎯 Бот РАБОТАЕТ! Тест успешен!")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ Токен не найден!")
        return
    
    logger.info("🤖 Запускаю бота...")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    
    logger.info("✅ Бот запущен и слушает сообщения...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
