import os
import asyncio
import logging
import threading
from flask import Flask
from telegram_bot import HotWheelsMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
monitor = None

@app.route('/')
def home():
    return "✅ HotWheels Bot is running!"

@app.route('/health')
def health():
    return "🟢 OK"

def run_bot():
    """Запуск Telegram бота"""
    global monitor
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found")
            return False
            
        monitor = HotWheelsMonitor(token)
        
        # Запускаем бота в отдельном потоке
        def start_bot():
            asyncio.run(monitor.start_bot())
        
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        logger.info("✅ Telegram Bot запущен!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        return False

# Запускаем бот
if run_bot():
    logger.info("🎉 Приложение запущено успешно!")
else:
    logger.error("💥 Не удалось запустить приложение")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port)
