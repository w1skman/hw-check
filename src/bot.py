import sqlite3
import requests
import os
import logging
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
        self.bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.init_db()
        
        # СПИСОК ТОВАРОВ ДЛЯ МОНИТОРИНГА
        self.products = [
            {
                'id': 'hw_basic', 
                'name': 'Hot Wheels Basic Car',
                'url': 'https://lenta.com/product/...',  # ЗАМЕНИ НА РЕАЛЬНЫЙ URL
                'store': 'Лента'
            },
            # Добавь другие товары здесь
        ]

    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect('hotwheels.db')
        cursor = conn.cursor()
        
        # Таблица истории остатков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                store_id TEXT,
                quantity INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица уведомлений
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

    def get_current_stock(self, product_url):
        """
        ЗАГЛУШКА - ЗАМЕНИ НА РЕАЛЬНЫЙ ПАРСИНГ
        """
        try:
            # TODO: Реальный парсинг сайта Ленты
            # Пример структуры для парсинга:
            # headers = {
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            # }
            # response = requests.get(product_url, headers=headers)
            # return parse_stock_from_html(response.text)
            
            # Заглушка для теста
            import random
            stock = random.randint(0, 10)
            logger.info(f"📦 Получен остаток: {stock} (заглушка)")
            return stock
            
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга: {e}")
            return None

    def check_all_products(self):
        """Проверка всех товаров"""
        conn = sqlite3.connect('hotwheels.db')
        cursor = conn.cursor()
        
        for product in self.products:
            logger.info(f"🔍 Проверка товара: {product['name']}")
            
            current_stock = self.get_current_stock(product['url'])
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
                f"\nДля отключения уведомлений настройте мониторинг."
            )
            
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )
            
            logger.info("📤 Уведомление отправлено в Telegram")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления: {e}")

def main():
    """Основная функция"""
    logger.info("🎬 Запуск мониторинга Hot Wheels...")
    monitor = HotWheelsMonitor()
    monitor.check_all_products()
    logger.info("🏁 Мониторинг завершен")

if __name__ == "__main__":
    main()
