#!/usr/bin/env python3
"""
Скрипт для завантаження Vosk моделі української мови
"""

import os
import requests
import zipfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_vosk_model():
    """Завантажує Vosk модель для української мови"""
    
    model_name = "vosk-model-small-uk"
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-uk-0.22.zip"
    
    # Перевіряємо, чи модель вже завантажена
    if os.path.exists(model_name):
        logger.info(f"Модель {model_name} вже існує")
        return True
    
    try:
        logger.info(f"Завантажуємо модель {model_name}...")
        
        # Завантажуємо файл
        response = requests.get(model_url, stream=True)
        response.raise_for_status()
        
        # Зберігаємо zip файл
        zip_path = f"{model_name}.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info("Розпаковуємо модель...")
        
        # Розпаковуємо
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')
        
        # Видаляємо zip файл
        os.remove(zip_path)
        
        logger.info(f"Модель {model_name} успішно завантажена!")
        return True
        
    except Exception as e:
        logger.error(f"Помилка завантаження моделі: {e}")
        return False

if __name__ == '__main__':
    download_vosk_model() 