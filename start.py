import os
import logging
import sys

# Додаємо поточну директорію до Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Імпортуємо наш aifc модуль перед speech_recognition
import aifc

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from voice_bot import VoiceBot

# Завантажуємо змінні середовища
load_dotenv()

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Створюємо Flask додаток
app = Flask(__name__)

# Створюємо екземпляр бота
bot = VoiceBot()

@app.route('/')
def home():
    """Головна сторінка"""
    return jsonify({
        "status": "running",
        "bot": "VoiceBotUA",
        "message": "Бот готовий до роботи!",
        "version": "1.0.0"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook для Telegram"""
    try:
        # Отримуємо дані від Telegram
        update = request.get_json()
        logger.info(f"Отримано оновлення: {update}")
        
        # Обробляємо оновлення
        bot.handle_update(update)
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Помилка обробки webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/set-webhook', methods=['GET'])
def set_webhook():
    """Встановлення webhook"""
    try:
        webhook_url = request.args.get('url')
        if not webhook_url:
            return jsonify({"error": "URL не надано"}), 400
        
        # Встановлюємо webhook
        bot.set_webhook(webhook_url)
        return jsonify({"status": "webhook set", "url": webhook_url})
        
    except Exception as e:
        logger.error(f"Помилка встановлення webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Запускаємо Flask сервер
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 