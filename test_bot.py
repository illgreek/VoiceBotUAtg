#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки конфігурації бота
"""

import os
from dotenv import load_dotenv

def test_configuration():
    """Перевіряє конфігурацію бота"""
    print("🔍 Перевірка конфігурації бота...")
    
    # Завантажуємо змінні середовища
    load_dotenv()
    
    # Перевіряємо токен
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN не знайдено!")
        print("📝 Створіть файл .env з вашим токеном:")
        print("   cp config.env.example .env")
        print("   # Відредагуйте .env та додайте ваш токен")
        return False
    
    if bot_token == 'your_bot_token_here':
        print("❌ BOT_TOKEN не налаштований!")
        print("📝 Замініть 'your_bot_token_here' на ваш справжній токен у файлі .env")
        return False
    
    print("✅ BOT_TOKEN налаштований правильно")
    
    # Перевіряємо залежності
    try:
        import speech_recognition
        print("✅ SpeechRecognition встановлено")
    except ImportError:
        print("❌ SpeechRecognition не встановлено")
        return False
    
    try:
        import pydub
        print("✅ pydub встановлено")
    except ImportError:
        print("❌ pydub не встановлено")
        return False
    
    try:
        from telegram import Bot
        print("✅ python-telegram-bot встановлено")
    except ImportError:
        print("❌ python-telegram-bot не встановлено")
        return False
    
    # Перевіряємо FFmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg встановлено")
        else:
            print("❌ FFmpeg не працює правильно")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ FFmpeg не знайдено")
        print("📝 Встановіть FFmpeg: brew install ffmpeg")
        return False
    
    print("\n🎉 Всі перевірки пройшли успішно!")
    print("🚀 Бот готовий до запуску!")
    print("💡 Запустіть бота командою: python3 voice_bot.py")
    
    return True

if __name__ == '__main__':
    test_configuration() 