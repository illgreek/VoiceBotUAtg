import os
import logging
import tempfile
import asyncio
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
import requests
import soundfile as sf
import numpy as np

# Vosk для розпізнавання мови
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk не встановлений, використовуємо fallback")

# Завантажуємо змінні середовища
load_dotenv()

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VoiceBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не знайдено в змінних середовища!")
        
        # Ініціалізуємо Vosk модель
        self.model = None
        if VOSK_AVAILABLE:
            try:
                # Завантажуємо модель для української мови
                model_path = os.path.join(os.path.dirname(__file__), 'vosk-model-small-uk')
                if os.path.exists(model_path):
                    self.model = Model(model_path)
                    logger.info("Vosk модель завантажена успішно")
                else:
                    logger.warning("Vosk модель не знайдена, використовуємо fallback")
            except Exception as e:
                logger.error(f"Помилка завантаження Vosk моделі: {e}")
        
        # Створюємо додаток для webhook
        self.application = Application.builder().token(self.bot_token).build()
        
        # Додаємо обробники
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /start"""
        welcome_message = """
🎤 Вітаю! Я бот для перетворення голосу в текст.

📝 Що я вмію:
• Перетворювати голосові повідомлення в текст
• Розпізнавати українську мову
• Обробляти аудіо файли та відео
• Автоматично працювати в групах

💡 Просто надішліть голосове повідомлення, і я перетворю його в текст!

/help - показати цю довідку
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /help"""
        help_text = """
🤖 Довідка по боту:

📱 Як користуватися:
1. Надішліть голосове повідомлення, аудіо файл або відео
2. Дочекайтеся обробки (може зайняти кілька секунд)
3. Отримайте текст вашого повідомлення

🏠 В приватних чатах:
• Бот відповідає на всі повідомлення

👥 В групах:
• Бот автоматично обробляє голосові повідомлення
• Показує ім'я користувача, який надіслав повідомлення
• Не відповідає на текстові повідомлення

⚙️ Налаштування:
• Мова розпізнавання: Українська
• Формати: OGG, MP3, WAV, MP4 (відео)

❓ Проблеми:
• Переконайтеся, що мова чітка
• Перевірте якість аудіо
• Спробуйте ще раз, якщо не спрацювало

/start - головне меню
        """
        await update.message.reply_text(help_text)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник голосових повідомлень"""
        try:
            # Перевіряємо, чи це група
            chat_type = update.effective_chat.type
            is_group = chat_type in ['group', 'supergroup']
            
            # Визначаємо, кому відповідати
            if is_group:
                # В групах відповідаємо на повідомлення
                processing_msg = await update.message.reply_text("🔄 Обробляю голосове повідомлення...")
            else:
                # В приватних чатах відправляємо нове повідомлення
                processing_msg = await update.message.reply_text("🔄 Обробляю голосове повідомлення...")
            
            # Отримуємо файл
            voice_file = await context.bot.get_file(update.message.voice.file_id)
            
            # Створюємо тимчасовий файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                # Завантажуємо аудіо
                voice_data = requests.get(voice_file.file_path).content
                temp_file.write(voice_data)
                temp_file_path = temp_file.name
            
            # Розпізнаємо мову за допомогою Vosk
            text = self.recognize_speech(temp_file_path)
            
            # Видаляємо тимчасовий файл
            os.unlink(temp_file_path)
            
            # Формуємо відповідь
            user_name = update.effective_user.first_name
            if is_group:
                response_text = f"📝 **{user_name}** каже:\n\n{text}"
            else:
                response_text = f"📝 Розпізнаний текст:\n\n{text}"
            
            # Відправляємо результат
            await processing_msg.edit_text(response_text, parse_mode='Markdown')
            
        except Exception as e:
            error_msg = "❌ Не вдалося розпізнати мову. Спробуйте ще раз з більш чіткою мовою."
            if is_group:
                await processing_msg.edit_text(error_msg)
            else:
                await processing_msg.delete()
                await update.message.reply_text(error_msg)
            logger.error(f"Помилка розпізнавання голосу: {e}")
        
        except Exception as e:
            error_msg = "❌ Сталася помилка при обробці голосового повідомлення."
            if is_group:
                await processing_msg.edit_text(error_msg)
            else:
                await processing_msg.delete()
                await update.message.reply_text(error_msg)
            logger.error(f"Помилка обробки голосу: {e}")
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник аудіо файлів"""
        try:
            # Перевіряємо, чи це група
            chat_type = update.effective_chat.type
            is_group = chat_type in ['group', 'supergroup']
            
            # Визначаємо, кому відповідати
            if is_group:
                processing_msg = await update.message.reply_text("🔄 Обробляю аудіо файл...")
            else:
                processing_msg = await update.message.reply_text("🔄 Обробляю аудіо файл...")
            
            # Отримуємо файл
            audio_file = await context.bot.get_file(update.message.audio.file_id)
            
            # Визначаємо розширення файлу
            file_name = update.message.audio.file_name or "audio"
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Створюємо тимчасовий файл
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                audio_data = requests.get(audio_file.file_path).content
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Конвертуємо в WAV
            if file_ext == '.ogg':
                audio = AudioSegment.from_ogg(temp_file_path)
            elif file_ext == '.mp3':
                audio = AudioSegment.from_mp3(temp_file_path)
            else:
                audio = AudioSegment.from_file(temp_file_path)
            
            wav_path = temp_file_path.replace(file_ext, '.wav')
            audio.export(wav_path, format='wav')
            
            # Розпізнаємо мову
            with sr.AudioFile(wav_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=self.language)
            
            # Видаляємо тимчасові файли
            os.unlink(temp_file_path)
            os.unlink(wav_path)
            
            # Формуємо відповідь
            user_name = update.effective_user.first_name
            if is_group:
                response_text = f"📝 **{user_name}** каже:\n\n{text}"
            else:
                response_text = f"📝 Розпізнаний текст:\n\n{text}"
            
            # Відправляємо результат
            await processing_msg.edit_text(response_text, parse_mode='Markdown')
            
        except Exception as e:
            error_msg = "❌ Сталася помилка при обробці аудіо файлу."
            if is_group:
                await processing_msg.edit_text(error_msg)
            else:
                await processing_msg.delete()
                await update.message.reply_text(error_msg)
            logger.error(f"Помилка обробки аудіо: {e}")
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник відео повідомлень (витягує аудіо)"""
        try:
            # Перевіряємо, чи це група
            chat_type = update.effective_chat.type
            is_group = chat_type in ['group', 'supergroup']
            
            # Визначаємо, кому відповідати
            if is_group:
                processing_msg = await update.message.reply_text("🔄 Обробляю відео та витягую аудіо...")
            else:
                processing_msg = await update.message.reply_text("🔄 Обробляю відео та витягую аудіо...")
            
            # Отримуємо файл
            video_file = await context.bot.get_file(update.message.video.file_id)
            
            # Створюємо тимчасовий файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                video_data = requests.get(video_file.file_path).content
                temp_file.write(video_data)
                temp_file_path = temp_file.name
            
            # Витягуємо аудіо з відео
            audio_path = temp_file_path.replace('.mp4', '.wav')
            audio = AudioSegment.from_file(temp_file_path)
            audio.export(audio_path, format='wav')
            
            # Розпізнаємо мову
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language=self.language)
            
            # Видаляємо тимчасові файли
            os.unlink(temp_file_path)
            os.unlink(audio_path)
            
            # Формуємо відповідь
            user_name = update.effective_user.first_name
            if is_group:
                response_text = f"📝 **{user_name}** каже у відео:\n\n{text}"
            else:
                response_text = f"📝 Розпізнаний текст з відео:\n\n{text}"
            
            # Відправляємо результат
            await processing_msg.edit_text(response_text, parse_mode='Markdown')
            
        except Exception as e:
            error_msg = "❌ Сталася помилка при обробці відео або немає аудіо."
            if is_group:
                await processing_msg.edit_text(error_msg)
            else:
                await processing_msg.delete()
                await update.message.reply_text(error_msg)
            logger.error(f"Помилка обробки відео: {e}")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник текстових повідомлень"""
        # В групах не відповідаємо на текстові повідомлення
        chat_type = update.effective_chat.type
        if chat_type in ['group', 'supergroup']:
            return
        
        await update.message.reply_text(
            "🎤 Надішліть мені голосове повідомлення, і я перетворю його в текст!\n\n"
            "💡 Підтримуються формати: OGG, MP3, WAV, MP4 (відео)"
        )
    
    def handle_update(self, update_dict):
        """Обробка оновлення від webhook"""
        try:
            # Конвертуємо dict в Update об'єкт
            update = Update.de_json(update_dict, self.application.bot)
            
            # Запускаємо обробку асинхронно
            asyncio.run(self.application.process_update(update))
            
        except Exception as e:
            logger.error(f"Помилка обробки оновлення: {e}")
    
    def recognize_speech(self, audio_path):
        """Розпізнавання мови за допомогою Vosk"""
        try:
            if not self.model:
                return "❌ Модель розпізнавання мови не завантажена"
            
            # Конвертуємо аудіо в WAV формат
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.replace('.ogg', '.wav').replace('.mp3', '.wav').replace('.m4a', '.wav')
            audio.export(wav_path, format='wav')
            
            # Читаємо аудіо файл
            data, sample_rate = sf.read(wav_path)
            
            # Створюємо розпізнавач
            rec = KaldiRecognizer(self.model, sample_rate)
            rec.SetWords(True)
            
            # Розпізнаємо мову
            rec.AcceptWaveform(data.tobytes())
            result = json.loads(rec.FinalResult())
            
            # Видаляємо тимчасовий файл
            if os.path.exists(wav_path):
                os.unlink(wav_path)
            
            text = result.get('text', '').strip()
            if text:
                return text
            else:
                return "❌ Не вдалося розпізнати мову"
                
        except Exception as e:
            logger.error(f"Помилка розпізнавання мови: {e}")
            return f"❌ Помилка розпізнавання: {str(e)}"
    
    def set_webhook(self, webhook_url):
        """Встановлення webhook"""
        try:
            webhook_url = f"{webhook_url}/webhook"
            result = self.application.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook встановлено: {webhook_url}")
            return result
        except Exception as e:
            logger.error(f"Помилка встановлення webhook: {e}")
            raise e
    
    def run(self):
        """Запуск бота в режимі polling"""
        logger.info("Бот запущений в режимі polling!")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    bot = VoiceBot()
    bot.run() 