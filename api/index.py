import os
import json
import logging
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv
import requests

# Завантажуємо змінні середовища
load_dotenv()

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обробка GET запитів"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        bot_token = os.getenv('BOT_TOKEN')
        
        response = {
            "status": "running",
            "bot": "VoiceBotUA",
            "message": "Бот готовий до роботи!",
            "url": "https://t.me/VoiceToTextUA_bot",
            "token_status": "configured" if bot_token else "missing",
            "version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
    
    def do_POST(self):
        """Обробка POST запитів від Telegram"""
        try:
            # Отримуємо дані від Telegram
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update = json.loads(post_data.decode('utf-8'))
            
            logger.info(f"Отримано оновлення: {update}")
            
            # Обробляємо повідомлення
            self.handle_update(update)
            
            # Відповідаємо Telegram
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        except Exception as e:
            logger.error(f"Помилка обробки запиту: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def handle_update(self, update):
        """Обробка оновлення від Telegram"""
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            logger.error("BOT_TOKEN не налаштований")
            return
        
        # Перевіряємо, чи є повідомлення
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        message_type = message.get('chat', {}).get('type', 'private')
        
        # Обробляємо команди
        if 'text' in message:
            text = message['text']
            if text == '/start':
                self.send_message(chat_id, self.get_start_message())
            elif text == '/help':
                self.send_message(chat_id, self.get_help_message())
            else:
                self.send_message(chat_id, "Надішліть голосове повідомлення для конвертації в текст.")
        
        # Обробляємо голосові повідомлення
        elif 'voice' in message:
            self.handle_voice_message(message, chat_id, message_type)
        
        # Обробляємо аудіо файли
        elif 'audio' in message:
            self.handle_audio_message(message, chat_id, message_type)
        
        # Обробляємо відео
        elif 'video' in message:
            self.handle_video_message(message, chat_id, message_type)
    
    def handle_voice_message(self, message, chat_id, message_type):
        """Обробка голосових повідомлень"""
        voice = message['voice']
        file_id = voice['file_id']
        
        # Отримуємо інформацію про файл
        file_info = self.get_file_info(file_id)
        if not file_info:
            self.send_message(chat_id, "❌ Помилка отримання файлу")
            return
        
        # Скачуємо файл
        file_path = self.download_file(file_info['file_path'])
        if not file_path:
            self.send_message(chat_id, "❌ Помилка завантаження файлу")
            return
        
        # Конвертуємо в текст (спрощена версія)
        try:
            # Тут буде логіка розпізнавання мови
            recognized_text = "🎤 Голосове повідомлення отримано!\n\n⚠️ Розпізнавання мови тимчасово недоступне на Vercel.\n\nДля повної функціональності запустіть бота локально або на іншому сервері."
            
            # Формуємо відповідь
            if message_type == 'group' or message_type == 'supergroup':
                username = message.get('from', {}).get('username', 'Користувач')
                response_text = f"@{username}\n\n{recognized_text}"
            else:
                response_text = recognized_text
            
            self.send_message(chat_id, response_text)
            
        except Exception as e:
            logger.error(f"Помилка розпізнавання: {e}")
            self.send_message(chat_id, "❌ Помилка розпізнавання мови")
    
    def handle_audio_message(self, message, chat_id, message_type):
        """Обробка аудіо файлів"""
        self.send_message(chat_id, "🎵 Аудіо файл отримано!\n\n⚠️ Розпізнавання мови тимчасово недоступне на Vercel.")
    
    def handle_video_message(self, message, chat_id, message_type):
        """Обробка відео повідомлень"""
        self.send_message(chat_id, "🎬 Відео отримано!\n\n⚠️ Розпізнавання мови тимчасово недоступне на Vercel.")
    
    def get_file_info(self, file_id):
        """Отримання інформації про файл"""
        bot_token = os.getenv('BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/getFile"
        params = {"file_id": file_id}
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()['result']
        except Exception as e:
            logger.error(f"Помилка отримання інформації про файл: {e}")
        
        return None
    
    def download_file(self, file_path):
        """Завантаження файлу"""
        bot_token = os.getenv('BOT_TOKEN')
        url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # В реальному боті тут буде збереження файлу
                return "temp_file.ogg"
        except Exception as e:
            logger.error(f"Помилка завантаження файлу: {e}")
        
        return None
    
    def send_message(self, chat_id, text):
        """Відправка повідомлення"""
        bot_token = os.getenv('BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code != 200:
                logger.error(f"Помилка відправки повідомлення: {response.text}")
        except Exception as e:
            logger.error(f"Помилка відправки повідомлення: {e}")
    
    def get_start_message(self):
        """Повідомлення для команди /start"""
        return """🎤 <b>VoiceBotUA - Конвертер голосу в текст</b>

<b>Як користуватися:</b>
1️⃣ Надішліть голосове повідомлення
2️⃣ Дочекайтеся обробки (може зайняти кілька секунд)
3️⃣ Отримайте текст вашого повідомлення

<b>Налаштування:</b>
• Мова розпізнавання: Українська
• Формат: OGG, MP3, WAV

<b>Проблеми:</b>
• Переконайтеся, що мова чітка
• Перевірте якість аудіо
• Спробуйте ще раз, якщо не спрацювало

/start - головне меню
/help - допомога"""
    
    def get_help_message(self):
        """Повідомлення для команди /help"""
        return """❓ <b>Допомога по боту</b>

<b>Підтримувані формати:</b>
• Голосові повідомлення
• Аудіо файли
• Відео з аудіо

<b>Мови:</b>
• Українська (основна)

<b>Команди:</b>
/start - головне меню
/help - ця довідка

<b>Для груп:</b>
Бот автоматично відповідає на голосові повідомлення в групах.

<b>Проблеми?</b>
Переконайтеся, що:
• Аудіо чітке
• Мова українська
• Файл не пошкоджений"""

# Тестова функція
def test_bot():
    """Тестування бота"""
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token:
        return f"✅ Бот налаштований правильно! Токен: {bot_token[:10]}..."
    else:
        return "❌ BOT_TOKEN не знайдено"

if __name__ == '__main__':
    print(test_bot()) 