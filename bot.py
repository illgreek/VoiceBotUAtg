import os
import logging
import tempfile
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from pydub import AudioSegment

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
        
        # Завантаження Faster Whisper моделі
        logger.info("Завантаження Faster Whisper моделі...")
        self.whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Faster Whisper модель завантажена")
        
        # Налаштування обробників повідомлень
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
        self.application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        logger.info("VoiceBot ініціалізовано")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка голосових повідомлень"""
        try:
            await update.message.reply_text("🎵 Обробляю голосове повідомлення...")
            
            # Отримання файлу
            voice_file = await context.bot.get_file(update.message.voice.file_id)
            
            # Завантаження та конвертація
            audio_file_path = await self.download_and_convert_audio(voice_file.file_path)
            
            if audio_file_path:
                try:
                    # Розпізнавання мови
                    text = await self.recognize_speech(audio_file_path)
                    if text:
                        await update.message.reply_text(f"📝 **Розпізнаний текст:**\n\n{text}")
                    else:
                        await update.message.reply_text("❌ Не вдалося розпізнати мову")
                finally:
                    # Видалення тимчасового WAV файлу
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            else:
                await update.message.reply_text("❌ Помилка обробки аудіо")
                
        except Exception as e:
            logger.error(f"Помилка обробки голосового повідомлення: {e}")
            await update.message.reply_text("❌ Помилка обробки голосового повідомлення")
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка аудіо файлів"""
        try:
            await update.message.reply_text("🎵 Обробляю аудіо файл...")
            
            audio_file = await context.bot.get_file(update.message.audio.file_id)
            audio_file_path = await self.download_and_convert_audio(audio_file.file_path)
            
            if audio_file_path:
                try:
                    text = await self.recognize_speech(audio_file_path)
                    if text:
                        await update.message.reply_text(f"📝 **Розпізнаний текст:**\n\n{text}")
                    else:
                        await update.message.reply_text("❌ Не вдалося розпізнати мову")
                finally:
                    # Видалення тимчасового WAV файлу
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            else:
                await update.message.reply_text("❌ Помилка обробки аудіо")
                
        except Exception as e:
            logger.error(f"Помилка обробки аудіо файлу: {e}")
            await update.message.reply_text("❌ Помилка обробки аудіо файлу")
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка відео файлів (тільки аудіо)"""
        try:
            await update.message.reply_text("🎬 Обробляю аудіо з відео...")
            
            video_file = await context.bot.get_file(update.message.video.file_id)
            audio_file_path = await self.download_and_convert_audio(video_file.file_path)
            
            if audio_file_path:
                try:
                    text = await self.recognize_speech(audio_file_path)
                    if text:
                        await update.message.reply_text(f"📝 **Розпізнаний текст:**\n\n{text}")
                    else:
                        await update.message.reply_text("❌ Не вдалося розпізнати мову")
                finally:
                    # Видалення тимчасового WAV файлу
                    if os.path.exists(audio_file_path):
                        os.unlink(audio_file_path)
            else:
                await update.message.reply_text("❌ Помилка обробки аудіо з відео")
                
        except Exception as e:
            logger.error(f"Помилка обробки відео: {e}")
            await update.message.reply_text("❌ Помилка обробки відео")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробка текстових повідомлень"""
        # Перевіряємо, чи це приватний чат (не група)
        if update.message.chat.type == "private":
            text = update.message.text
            await update.message.reply_text(
                f"👋 Привіт! Я бот для розпізнавання мови.\n\n"
                f"📤 Надішліть мені голосове повідомлення, аудіо або відео файл, "
                f"і я перетворю його в текст.\n\n"
                f"🇺🇦 Підтримую українську мову!"
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
        """Розпізнавання мови за допомогою Faster Whisper"""
        try:
            logger.info("Початок розпізнавання з Faster Whisper")
            
            # Розпізнавання з Faster Whisper
            segments, info = self.whisper_model.transcribe(
                audio_file_path,
                language="uk",  # Вказуємо українську мову
                beam_size=5
            )
            
            # Збираємо текст з сегментів
            text = " ".join([segment.text for segment in segments]).strip()
            detected_language = info.language
            
            logger.info(f"Faster Whisper розпізнав мову: {detected_language}")
            logger.info(f"Розпізнаний текст: {text}")
            
            if text:
                return text
            else:
                logger.warning("Faster Whisper повернув порожній текст")
                return None
                
        except Exception as e:
            logger.error(f"Помилка розпізнавання з Faster Whisper: {e}")
            return None
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск VoiceBot...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = VoiceBot()
    bot.run() 