#!/usr/bin/env python3
"""
Скрипт для налаштування webhook після деплою на Render
"""

import os
import requests
from dotenv import load_dotenv

# Завантажуємо змінні середовища
load_dotenv()

def setup_webhook():
    """Налаштування webhook для Telegram бота"""
    
    # Отримуємо токен бота
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не знайдено в змінних середовища!")
        print("Додайте BOT_TOKEN в файл .env")
        return False
    
    # Запитуємо URL сервісу
    print("🌐 Введіть URL вашого сервісу на Render:")
    print("Приклад: https://voicebot-ua.onrender.com")
    webhook_url = input("URL: ").strip()
    
    if not webhook_url:
        print("❌ URL не може бути порожнім!")
        return False
    
    # Формуємо повний URL для webhook
    full_webhook_url = f"{webhook_url}/webhook"
    
    # URL для встановлення webhook
    telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    try:
        # Встановлюємо webhook
        response = requests.post(telegram_api_url, json={
            "url": full_webhook_url,
            "allowed_updates": ["message", "edited_message"]
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook успішно встановлено!")
                print(f"🌐 URL: {full_webhook_url}")
                print(f"📊 Статус: {result.get('description', 'OK')}")
                return True
            else:
                print(f"❌ Помилка встановлення webhook: {result.get('description')}")
                return False
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            print(f"Відповідь: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def check_webhook():
    """Перевірка поточного webhook"""
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не знайдено!")
        return False
    
    try:
        # Отримуємо інформацію про webhook
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
                
                print("📊 Інформація про webhook:")
                print(f"URL: {webhook_info.get('url', 'Не встановлено')}")
                print(f"Статус: {'✅ Активний' if webhook_info.get('url') else '❌ Не встановлено'}")
                
                if webhook_info.get('last_error_date'):
                    print(f"Остання помилка: {webhook_info.get('last_error_message')}")
                
                return webhook_info.get('url') is not None
            else:
                print(f"❌ Помилка отримання інформації: {result.get('description')}")
                return False
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def delete_webhook():
    """Видалення webhook"""
    
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не знайдено!")
        return False
    
    try:
        # Видаляємо webhook
        response = requests.post(f"https://api.telegram.org/bot{bot_token}/deleteWebhook")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Webhook успішно видалено!")
                return True
            else:
                print(f"❌ Помилка видалення: {result.get('description')}")
                return False
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def main():
    """Головна функція"""
    
    print("🤖 Налаштування webhook для Telegram бота")
    print("=" * 50)
    
    while True:
        print("\n📋 Виберіть опцію:")
        print("1. Встановити webhook")
        print("2. Перевірити webhook")
        print("3. Видалити webhook")
        print("4. Вихід")
        
        choice = input("\nВаш вибір (1-4): ").strip()
        
        if choice == '1':
            setup_webhook()
        elif choice == '2':
            check_webhook()
        elif choice == '3':
            delete_webhook()
        elif choice == '4':
            print("👋 До побачення!")
            break
        else:
            print("❌ Невірний вибір! Спробуйте ще раз.")

if __name__ == '__main__':
    main() 