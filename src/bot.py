import sqlite3
import requests
import os
import logging
import asyncio
from datetime import datetime
from telegram import Bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HotWheelsMonitor:
    def __init__(self):
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not token or not chat_id:
            logger.error("❌ Не найдены TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
            return
            
        self.bot = Bot(token=token)
        self.chat_id = int(chat_id)
        self.init_db()
        
        # СПИСОК ТОВАРОВ ДЛЯ МОНИТОРИНГА
        self.products = [
            {
                'id': 'hw_265193', 
                'name': 'Hot Wheels Basic Car',
                'product_id': '265193',  # ID товара из API
                'store_id': '3223',      # ID твоего магазина
                'store': 'Лента (твой магазин)'
            },
        ]

    def init_db(self):
        """Инициализация базы данных"""
        try:
            conn = sqlite3.connect('hotwheels.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT,
                    store_id TEXT,
                    quantity INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT,
                    old_quantity INTEGER,
                    new_quantity INTEGER,
                    increase INTEGER,
                    acknowledged BOOLEAN DEFAULT FALSE,
                    message_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ База данных инициализирована")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")

    def get_current_stock(self, product_id, store_id):
        """Получение остатка через API Ленты"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                'Origin': 'https://lenta.com',
                'Referer': 'https://lenta.com/',
            }
            
            params = {
                'id': product_id,
                'storeId': store_id
            }
            
            url = 'https://lenta.com/api-gateway/v1/catalog/items/stock'
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            stock = data.get('stock', 0)
            
            logger.info(f"📦 API Ленты: остаток {stock} шт. (product: {product_id}, store: {store_id})")
            return stock
            
        except Exception as e:
            logger.error(f"❌ Ошибка API Ленты: {e}")
            return None

    def check_all_products(self):
        """Проверка всех товаров"""
        try:
            conn = sqlite3.connect('hotwheels.db')
            cursor = conn.cursor()
            
            for product in self.products:
                logger.info(f"🔍 Проверка товара: {product['name']}")
                
                current_stock = self.get_current_stock(product['product_id'], product['store_id'])
                if current_stock is None:
                    continue
                
                # Получаем предыдущий остаток из БД
                cursor.execute('''
                    SELECT quantity FROM stock_history 
                    WHERE product_id = ? 
                    ORDER BY timestamp DESC LIMIT 1
                ''', (product['id'],))
                
                result = cursor.fetchone()
                previous_stock = result[0] if result else 0
                
                # Сохраняем текущий остаток
                cursor.execute('''
                    INSERT INTO stock_history (product_id, store_id, quantity)
                    VALUES (?, ?, ?)
                ''', (product['id'], product['store'], current_stock))
                
                # Проверяем увеличение остатка
                if current_stock > previous_stock:
                    increase = current_stock - previous_stock
                    logger.info(f"🚨 ОБНАРУЖЕНО УВЕЛИЧЕНИЕ: +{increase} шт.")
                    self.send_notification(product, previous_stock, current_stock, increase)
                else:
                    logger.info(f"✅ Изменений нет: {previous_stock} → {current_stock}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки товаров: {e}")

    def send_notification(self, product, old_qty, new_qty, increase):
        """Отправка уведомления в Telegram"""
        try:
            message = (
                f"🚨 HOT WHEELS ALERT!\n"
                f"🎯 {product['name']}\n"
                f"🏪 {product['store']}\n"
                f"📊 Было: {old_qty} → Стало: {new_qty}\n"
                f"📈 Прирост: +{increase} шт.\n"
                f"⏰ {datetime.now().strftime('%H:%M %d.%m.%Y')}\n"
                f"\nСкорее беги в магазин! 🏃‍♂️"
            )
            
            asyncio.run(self.bot.send_message(
                chat_id=self.chat_id,
                text=message
            ))
            
            logger.info("📤 Уведомление отправлено в Telegram")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления: {e}")

def main():
    """Основная функция"""
    try:
        logger.info("🎬 Запуск мониторинга Hot Wheels...")
        monitor = HotWheelsMonitor()
        monitor.check_all_products()
        logger.info("🏁 Мониторинг завершен")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
