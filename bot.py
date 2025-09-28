import os
import asyncio
import logging
from flask import Flask

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ HotWheels Bot is running!"

@app.route('/health')
def health():
    return "🟢 OK"

def run_bot():
    """Запуск Telegram бота"""
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found")
            return False
            
        # Импортируем здесь чтобы избежать циклических импортов
        from telegram_bot import HotWheelsMonitor
        monitor = HotWheelsMonitor(token)
        
        # Запускаем бота в отдельном потоке
        def start_bot():
            asyncio.run(monitor.start_bot())
        
        import threading
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        logger.info("🤖 Telegram Bot started successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        return False

# Запускаем бот при старте приложения
bot_started = run_bot()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)
