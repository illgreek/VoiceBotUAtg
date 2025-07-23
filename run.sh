#!/bin/bash

echo "🤖 Запуск VoiceBot з Coqui TTS..."

# Перевіряємо чи є .env файл
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не знайдено!"
    echo "Створіть файл .env з вашим BOT_TOKEN"
    echo "Приклад:"
    echo "BOT_TOKEN=your_bot_token_here"
    exit 1
fi

# Встановлюємо залежності
echo "📦 Встановлення залежностей..."
pip3 install -r requirements.txt

# Запускаємо бота
echo "🚀 Запуск бота..."
python3 bot.py 