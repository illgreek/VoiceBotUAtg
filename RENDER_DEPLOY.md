# 🚀 Деплой Telegram бота на Render

Цей гід допоможе вам розгорнути Telegram бота для конвертації голосу в текст на платформі Render.

## 📋 Передумови

1. **Telegram Bot Token** - отримайте від @BotFather
2. **GitHub репозиторій** з кодом бота
3. **Обліковий запис на Render** (безкоштовний)

## 🛠️ Підготовка проекту

### Структура файлів:
```
VoiceBotUAtg/
├── voice_bot.py          # Основний код бота
├── start.py              # Flask сервер для webhook
├── requirements.txt      # Python залежності
├── render.yaml           # Конфігурація Render
├── .env                  # Змінні середовища (локально)
└── config.env.example    # Приклад конфігурації
```

### Необхідні файли:
- ✅ `voice_bot.py` - основний код бота
- ✅ `start.py` - Flask сервер
- ✅ `requirements.txt` - залежності
- ✅ `render.yaml` - конфігурація Render

## 🚀 Кроки деплою

### 1. Підготуйте репозиторій

```bash
# Переконайтеся, що всі файли додані до Git
git add .
git commit -m "Підготовка для деплою на Render"
git push origin main
```

### 2. Створіть обліковий запис на Render

1. Перейдіть на [render.com](https://render.com)
2. Зареєструйтесь через GitHub
3. Підтвердіть email

### 3. Деплой через Blueprint

1. **Відкрийте Render Dashboard**
2. **Натисніть "New +" → "Blueprint"**
3. **Підключіть GitHub репозиторій**
4. **Виберіть репозиторій з ботом**
5. **Render автоматично знайде `render.yaml`**

### 4. Налаштуйте змінні середовища

1. **Відкрийте створений сервіс**
2. **Перейдіть в "Environment"**
3. **Додайте змінну:**
   - **Key:** `BOT_TOKEN`
   - **Value:** ваш Telegram bot token

### 5. Запустіть деплой

1. **Натисніть "Create Blueprint Instance"**
2. **Дочекайтеся завершення деплою** (5-10 хвилин)
3. **Скопіюйте URL сервісу** (наприклад: `https://voicebot-ua.onrender.com`)

## 🔗 Налаштування Webhook

### Автоматичне налаштування:

Відкрийте в браузері:
```
https://your-app-name.onrender.com/set-webhook?url=https://your-app-name.onrender.com
```

### Ручне налаштування:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-app-name.onrender.com/webhook"}'
```

## ✅ Перевірка роботи

### 1. Перевірте статус бота:
```
https://your-app-name.onrender.com/
```

### 2. Протестуйте бота:
1. Відкрийте вашого бота в Telegram
2. Надішліть команду `/start`
3. Надішліть голосове повідомлення

## 🔧 Налаштування для груп

### 1. Додайте бота в групу
### 2. Надайте права на читання повідомлень
### 3. Бот автоматично оброблятиме голосові повідомлення

## 📊 Моніторинг

### Логи:
- Відкрийте сервіс в Render Dashboard
- Перейдіть в "Logs"
- Дивіться логи в реальному часі

### Статус:
- **Healthy** - бот працює
- **Unhealthy** - є проблеми

## 🆘 Вирішення проблем

### Помилка "Build Failed":
1. Перевірте `requirements.txt`
2. Переконайтеся, що всі залежності вказані
3. Дивіться логи збірки

### Бот не відповідає:
1. Перевірте webhook URL
2. Переконайтеся, що `BOT_TOKEN` встановлений
3. Перевірте логи сервісу

### Помилки з аудіо:
1. Перевірте, чи встановлений FFmpeg
2. Переконайтеся, що аудіо файл не пошкоджений
3. Спробуйте інший формат аудіо

## 💰 Вартість

- **Free план:** 750 годин/місяць
- **Після вичерпання:** $7/місяць
- **Рекомендація:** оновіться на Pro план для 24/7 роботи

## 🔄 Оновлення бота

```bash
# Внесіть зміни в код
git add .
git commit -m "Оновлення бота"
git push origin main

# Render автоматично перезапустить сервіс
```

## 📞 Підтримка

- **Render Docs:** [docs.render.com](https://docs.render.com)
- **Telegram Bot API:** [core.telegram.org/bots](https://core.telegram.org/bots)
- **GitHub Issues:** створіть issue в репозиторії

---

**🎉 Вітаємо! Ваш бот успішно розгорнутий на Render!**