import os
import logging
import tempfile
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from ukrainian_punctuation import improve_ukrainian_text

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Завантаження змінних середовища
load_dotenv()

class VoiceBot:
    def __init__(self):
        self.bot_token = os.getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("BOT_TOKEN не знайдено в .env файлі")
        
        self.application = Application.builder().token(self.bot_token).build()
        
        # Ініціалізація SpeechRecognition
        logger.info("Ініціалізація SpeechRecognition...")
        try:
            self.recognizer = sr.Recognizer()
            logger.info("SpeechRecognition ініціалізовано")
        except Exception as e:
            logger.error(f"Помилка ініціалізації SpeechRecognition: {e}")
            self.recognizer = None
        

        
        # Налаштування обробників повідомлень
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(filters.VIDEO_NOTE, self.handle_video_note))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        logger.info("VoiceBot з SpeechRecognition ініціалізовано")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка голосових повідомлень"""
        try:
            if not self.recognizer:
                await update.message.reply_text("❌ Розпізнавач не ініціалізований")
                return
            
            # Отримання файлу
            voice_file = await context.bot.get_file(update.message.voice.file_id)
            
            # Відправляємо повідомлення про обробку
            user_name = update.message.from_user.first_name or "Користувач"
            processing_msg = await update.message.reply_text(f"🎵 Обробляю голосове повідомлення від {user_name}...")
            
            # Завантаження та конвертація
            audio_file_path = await self.download_and_convert_audio(voice_file.file_path)
            
            if audio_file_path:
                try:
                    # Розпізнавання мови
                    text = await self.recognize_speech(audio_file_path)
                    if text:
                        # Редагуємо повідомлення з результатом
                        await processing_msg.edit_text(f"📝 **Розпізнаний текст від {user_name}:**\n\n{text}")
                    else:
                        await processing_msg.edit_text("❌ Не вдалося розпізнати мову")
                finally:
                    # Видалення тимчасового WAV файлу
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            else:
                await processing_msg.edit_text("❌ Помилка обробки аудіо")
                
        except Exception as e:
            logger.error(f"Помилка обробки голосового повідомлення: {e}")
            await update.message.reply_text("❌ Помилка обробки голосового повідомлення")
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка аудіо файлів"""
        try:
            if not self.recognizer:
                await update.message.reply_text("❌ Розпізнавач не ініціалізований")
                return
            
            audio_file = await context.bot.get_file(update.message.audio.file_id)
            
            # Відправляємо повідомлення про обробку
            user_name = update.message.from_user.first_name or "Користувач"
            processing_msg = await update.message.reply_text(f"🎵 Обробляю аудіо файл від {user_name}...")
            
            audio_file_path = await self.download_and_convert_audio(audio_file.file_path)
            
            if audio_file_path:
                try:
                    text = await self.recognize_speech(audio_file_path)
                    if text:
                        await processing_msg.edit_text(f"📝 **Розпізнаний текст від {user_name}:**\n\n{text}")
                    else:
                        await processing_msg.edit_text("❌ Не вдалося розпізнати мову")
                finally:
                    # Видалення тимчасового WAV файлу
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            else:
                await processing_msg.edit_text("❌ Помилка обробки аудіо")
                
        except Exception as e:
            logger.error(f"Помилка обробки аудіо файлу: {e}")
            await update.message.reply_text("❌ Помилка обробки аудіо файлу")
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка відео файлів (тільки аудіо)"""
        try:
            if not self.recognizer:
                await update.message.reply_text("❌ Розпізнавач не ініціалізований")
                return
            
            video_file = await context.bot.get_file(update.message.video.file_id)
            
            # Відправляємо повідомлення про обробку
            user_name = update.message.from_user.first_name or "Користувач"
            processing_msg = await update.message.reply_text(f"🎬 Обробляю аудіо з відео від {user_name}...")
            
            audio_file_path = await self.download_and_convert_audio(video_file.file_path)
            
            if audio_file_path:
                try:
                    text = await self.recognize_speech(audio_file_path)
                    if text:
                        await processing_msg.edit_text(f"📝 **Розпізнаний текст від {user_name}:**\n\n{text}")
                    else:
                        await processing_msg.edit_text("❌ Не вдалося розпізнати мову")
                finally:
                    # Видалення тимчасового WAV файлу
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            else:
                await processing_msg.edit_text("❌ Помилка обробки аудіо з відео")
                
        except Exception as e:
            logger.error(f"Помилка обробки відео: {e}")
            await update.message.reply_text("❌ Помилка обробки відео")
    
    async def handle_video_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка відео повідомлень (кружечки)"""
        try:
            if not self.recognizer:
                await update.message.reply_text("❌ Розпізнавач не ініціалізований")
                return
            
            video_note_file = await context.bot.get_file(update.message.video_note.file_id)
            
            # Відправляємо повідомлення про обробку
            user_name = update.message.from_user.first_name or "Користувач"
            processing_msg = await update.message.reply_text(f"🎬 Обробляю відео повідомлення від {user_name}...")
            
            audio_file_path = await self.download_and_convert_audio(video_note_file.file_path)
            
            if audio_file_path:
                try:
                    text = await self.recognize_speech(audio_file_path)
                    if text:
                        await processing_msg.edit_text(f"📝 **Розпізнаний текст від {user_name}:**\n\n{text}")
                    else:
                        await processing_msg.edit_text("❌ Не вдалося розпізнати мову")
                finally:
                    # Видалення тимчасового WAV файлу
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            else:
                await processing_msg.edit_text("❌ Помилка обробки аудіо з відео повідомлення")
                
        except Exception as e:
            logger.error(f"Помилка обробки відео повідомлення: {e}")
            await update.message.reply_text("❌ Помилка обробки відео повідомлення")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка текстових повідомлень"""
        # Перевіряємо, чи це приватний чат (не група)
        if update.message.chat.type == "private":
            await update.message.reply_text(
                f"👋 Привіт! Я бот для розпізнавання мови (Google Speech).\n\n"
                f"📤 Надішліть мені:\n"
                f"• 🎵 Голосове повідомлення\n"
                f"• 🎵 Аудіо файл\n"
                f"• 🎬 Відео файл\n"
                f"• 🎬 Відео повідомлення (кружечок)\n\n"
                f"🇺🇦 Підтримую українську мову!\n"
                f"🌐 Використовую Google Speech API"
            )
        # В групах бот не відповідає на текстові повідомлення
    
    async def download_and_convert_audio(self, file_path: str) -> str:
        """Завантаження та конвертація аудіо в WAV"""
        try:
            # Завантаження файлу
            response = requests.get(file_path)
            response.raise_for_status()
            
            # Збереження в тимчасовий файл
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Конвертація в WAV за допомогою pydub
            audio = AudioSegment.from_file(temp_file_path)
            
            # Експорт в WAV
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                audio.export(wav_file.name, format='wav')
                wav_path = wav_file.name
            
            # Видалення тимчасового OGG файлу
            os.unlink(temp_file_path)
            
            return wav_path
            
        except Exception as e:
            logger.error(f"Помилка конвертації аудіо: {e}")
            return None
    
    async def recognize_speech(self, audio_file_path: str) -> str:
        """Розпізнавання мови за допомогою Google Speech API"""
        try:
            logger.info("Початок розпізнавання з Google Speech API")
            
            # Читаємо аудіо файл
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Розпізнаємо текст
            text = self.recognizer.recognize_google(
                audio, 
                language='uk-UA'  # Українська мова
            )
            
            logger.info(f"Google Speech API розпізнав текст: {text}")
            
            if text and text.strip():
                # Покращуємо український текст
                text = improve_ukrainian_text(text.strip())
                return text
            else:
                logger.warning("Google Speech API повернув порожній текст")
                return None
                
        except sr.UnknownValueError:
            logger.warning("Google Speech API не зміг розпізнати мову")
            return None
        except sr.RequestError as e:
            logger.error(f"Помилка запиту до Google Speech API: {e}")
            return None
        except Exception as e:
            logger.error(f"Помилка розпізнавання з Google Speech API: {e}")
            return None
    

    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск VoiceBot з Google Speech API...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = VoiceBot()
    bot.run() 