import os
import json
from http.server import BaseHTTPRequestHandler
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обробка GET запитів"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Перевіряємо токен
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
        """Обробка POST запитів"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        try:
            # Проста перевірка конфігурації
            bot_token = os.getenv('BOT_TOKEN')
            
            if not bot_token:
                response = {
                    "status": "error", 
                    "message": "BOT_TOKEN не налаштований"
                }
            else:
                response = {
                    "status": "success", 
                    "message": "Бот готовий до роботи",
                    "bot_url": "https://t.me/VoiceToTextUA_bot",
                    "features": [
                        "Голосові повідомлення",
                        "Аудіо файли", 
                        "Відео з аудіо",
                        "Українська мова",
                        "Робота в групах"
                    ]
                }
                
        except Exception as e:
            response = {
                "status": "error", 
                "message": f"Помилка: {str(e)}"
            }
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

# Тестова функція для перевірки
def test_bot():
    """Тестування бота"""
    bot_token = os.getenv('BOT_TOKEN')
    if bot_token:
        return f"✅ Бот налаштований правильно! Токен: {bot_token[:10]}..."
    else:
        return "❌ BOT_TOKEN не знайдено"

if __name__ == '__main__':
    print(test_bot())
