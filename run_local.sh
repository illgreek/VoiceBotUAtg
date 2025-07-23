#!/bin/bash

echo "🤖 Запуск VoiceBot локально..."

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
pip install -r requirements.txt

# Запускаємо бота
echo "🚀 Запуск бота..."
python bot.py 