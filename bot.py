import os
import logging
import schedule
import time
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

def run_scheduled_monitoring():
    """Запуск автоматической проверки остатков"""
    try:
        logger.info("🔄 Запускаю автоматическую проверку...")
        # Здесь будет логика проверки и записи в БД
        # Пока заглушка
        logger.info("✅ Автопроверка завершена")
    except Exception as e:
        logger.error(f"❌ Ошибка автопроверки: {e}")

def run_scheduler():
    """Запуск планировщика"""
    logger.info("⏰ Инициализация планировщика...")
    
    # Проверка в 10:00 и 18:00 по МСК (07:00 и 15:00 UTC)
    schedule.every().day.at("07:00").do(run_scheduled_monitoring)
    schedule.every().day.at("15:00").do(run_scheduled_monitoring)
    
    logger.info("✅ Планировщик запущен")
    
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
        bot_thread = threading.Thread(target=monitor.start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        logger.info("✅ Telegram Bot запущен в отдельном потоке")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        return False

# Инициализация
logger.info("🎬 Запуск приложения...")

# Запускаем бота
if run_bot():
    # Запускаем планировщик в отдельном потоке
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    logger.info("✅ Планировщик запущен в отдельном потоке")
else:
    logger.error("❌ Не удалось запустить бота")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"🚀 Запуск Flask на порту {port}")
    app.run(host='0.0.0.0', port=port)
