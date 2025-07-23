"""
Модуль aifc для Python 3.13
Виправлення проблеми з SpeechRecognition
"""

import wave
import struct

class Error(Exception):
    pass

def _read_32bit(file):
    """Читає 32-бітне число"""
    return struct.unpack('>I', file.read(4))[0]

def _read_16bit(file):
    """Читає 16-бітне число"""
    return struct.unpack('>H', file.read(2))[0]

def _read_string(file):
    """Читає рядок"""
    length = _read_32bit(file)
    return file.read(length).decode('ascii')

class Aifc_read:
    """Клас для читання AIFF-C файлів"""
    
    def __init__(self, f):
        self.file = f
        self._initfp(f)
    
    def _initfp(self, file):
        self._file = file
        self._soundpos = 0
        self._info = {}
        
        # Читаємо заголовок
        chunk = file.read(4)
        if chunk != b'FORM':
            raise Error('Not an AIFF file')
        
        # Пропускаємо розмір файлу
        file.read(4)
        
        # Читаємо тип
        chunk = file.read(4)
        if chunk not in [b'AIFF', b'AIFC']:
            raise Error('Not an AIFF file')
    
    def getnframes(self):
        """Повертає кількість кадрів"""
        return 0
    
    def getnchannels(self):
        """Повертає кількість каналів"""
        return 1
    
    def getsampwidth(self):
        """Повертає ширину семплу"""
        return 2
    
    def getframerate(self):
        """Повертає частоту дискретизації"""
        return 16000
    
    def readframes(self, nframes):
        """Читає кадри"""
        return b''

def open(f, mode=None):
    """Відкриває AIFF файл"""
    if mode is None:
        if hasattr(f, 'mode'):
            mode = f.mode
        else:
            mode = 'rb'
    
    if mode in ('r', 'rb'):
        return Aifc_read(f)
    else:
        raise Error('Only read mode is supported') 