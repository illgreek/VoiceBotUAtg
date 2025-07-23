#!/bin/bash

# 🚀 Скрипт для розгортання бота на Vercel

echo "🎤 Розгортання VoiceBotUA на Vercel..."
echo ""

# Перевірка наявності Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI не встановлено"
    echo "📥 Встановіть: npm i -g vercel"
    exit 1
fi

# Перевірка наявності .env файлу
if [ ! -f .env ]; then
    echo "❌ Файл .env не знайдено"
    echo "📝 Створіть файл .env з вашим BOT_TOKEN"
    echo "BOT_TOKEN=8137094513:AAEl6bC6g9pNeuM2CeZI_bJRQBSjAdh70mo"
    exit 1
fi

echo "✅ Всі перевірки пройшли"
echo ""

# Розгортання на Vercel
echo "🚀 Розгортаємо проект..."
vercel --prod

echo ""
echo "🎉 Розгортання завершено!"
echo "📱 Ваш бот доступний: https://t.me/VoiceToTextUA_bot"
echo ""
echo "💡 Для перевірки статусу відкрийте URL проекту в браузері" 