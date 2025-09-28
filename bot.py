import os
import asyncio
import logging
import schedule
import time
import threading
from flask import Flask
from telegram_bot import HotWheelsMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Глобальный экземпляр монитора
monitor = None

@app.route('/')
def home():
    return "✅ HotWheels Bot is running!"

@app.route('/check-now')
def check_now():
    """Ручной запуск проверки (для планировщика)"""
    asyncio.run(monitor.run_scheduled_monitoring())
    return "✅ Check completed"

def run_scheduled_checks():
    """Запуск проверок по расписанию"""
    # Проверка в 10:00 и 18:00 по МСК (07:00 и 15:00 UTC)
    schedule.every().day.at("07:00").do(lambda: asyncio.run(monitor.run_scheduled_monitoring()))
    schedule.every().day.at("15:00").do(lambda: asyncio.run(monitor.run_scheduled_monitoring()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

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
        
        logger.info("🤖 Telegram Bot started successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        return False

# Запускаем все
bot_started = run_bot()

if bot_started:
    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduled_checks)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    logger.info("⏰ Scheduler started!")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"🚀 Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)
