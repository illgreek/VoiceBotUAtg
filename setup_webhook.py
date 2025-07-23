#!/usr/bin/env python3
"""
Скрипт для налаштування webhook для Telegram бота на Vercel
"""

import os
import requests
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

def setup_webhook():
    """Налаштування webhook для бота"""
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("❌ BOT_TOKEN не знайдено в .env файлі")
        return False
    
    # URL вашого Vercel деплою
    # Замініть на ваш реальний URL після деплою
    webhook_url = "https://your-project-name.vercel.app/api/index.py"
    
    # URL для встановлення webhook
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    data = {
        "url": webhook_url,
        "allowed_updates": ["message", "edited_message"]
    }
    
    try:
        print(f"🔗 Налаштовуємо webhook: {webhook_url}")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook успішно налаштовано!")
                print(f"📊 Результат: {result}")
                return True
            else:
                print(f"❌ Помилка налаштування webhook: {result}")
                return False
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            print(f"📄 Відповідь: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def delete_webhook():
    """Видалення webhook"""
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("❌ BOT_TOKEN не знайдено")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    try:
        print("🗑️ Видаляємо webhook...")
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook успішно видалено!")
                return True
            else:
                print(f"❌ Помилка видалення webhook: {result}")
                return False
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def get_webhook_info():
    """Отримання інформації про webhook"""
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("❌ BOT_TOKEN не знайдено")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    try:
        print("📊 Отримуємо інформацію про webhook...")
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result['result']
                print("✅ Інформація про webhook:")
                print(f"   URL: {webhook_info.get('url', 'Не встановлено')}")
                print(f"   Статус: {'Активний' if webhook_info.get('url') else 'Неактивний'}")
                print(f"   Помилки: {webhook_info.get('last_error_message', 'Немає')}")
                return True
            else:
                print(f"❌ Помилка отримання інформації: {result}")
                return False
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Налаштування webhook для VoiceBotUA")
    print("=" * 50)
    
    while True:
        print("\nВиберіть опцію:")
        print("1. Налаштувати webhook")
        print("2. Видалити webhook")
        print("3. Перевірити webhook")
        print("4. Вихід")
        
        choice = input("\nВаш вибір (1-4): ").strip()
        
        if choice == "1":
            setup_webhook()
        elif choice == "2":
            delete_webhook()
        elif choice == "3":
            get_webhook_info()
        elif choice == "4":
            print("👋 До побачення!")
            break
        else:
            print("❌ Невірний вибір. Спробуйте ще раз.") 