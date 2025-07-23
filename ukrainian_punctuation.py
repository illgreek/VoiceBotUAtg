import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class UkrainianPunctuationProcessor:
    """
    Професійний обробник розділових знаків для української мови
    """
    
    def __init__(self):
        # Слова, після яких зазвичай ставиться кома
        self.comma_after_words = {
            'так', 'ні', 'можливо', 'звичайно', 'звісно', 'авжеж', 'безумовно',
            'нарешті', 'наприклад', 'тобто', 'отже', 'однак', 'проте', 'зате',
            'по-перше', 'по-друге', 'по-третє', 'по-четверте', 'по-п\'яте',
            'по-шосте', 'по-сьоме', 'по-восьме', 'по-дев\'яте', 'по-десяте',
            'друже', 'брате', 'сестро', 'мамо', 'тату', 'бабусю', 'дідусю',
            'дівчино', 'хлопче', 'сину', 'дочко', 'друзі', 'колеги',
            'на жаль', 'на щастя', 'на диво', 'на превеликий жаль',
            'чесно кажучи', 'правду кажучи', 'взагалі-то', 'власне кажучи',
            'між іншим', 'до речі', 'до слова', 'до того ж', 'крім того',
            'більше того', 'тим більше', 'тим паче', 'особливо', 'головне',
            'найголовніше', 'насамперед', 'спочатку', 'потім', 'далі',
            'нарешті', 'врешті-решт', 'в кінці кінців', 'в підсумку',
            'коротше кажучи', 'одним словом', 'словом', 'значить',
            'виходить', 'отже', 'от і все', 'ось і все'
        }
        
        # Сполучники, перед якими ставиться кома
        self.comma_before_conjunctions = {
            'але', 'проте', 'однак', 'зате', 'а', 'і', 'або', 'чи',
            'якщо', 'якби', 'хоч', 'хоча', 'незважаючи на те що',
            'попри те що', 'замість того щоб', 'замість того аби',
            'щоб', 'аби', 'поки', 'доки', 'коли', 'як', 'як тільки',
            'щойно', 'лише', 'тільки', 'лишень', 'тільки що',
            'тому що', 'бо', 'оскільки', 'адже', 'аджеж',
            'що', 'який', 'яка', 'яке', 'які', 'хто', 'де', 'коли',
            'куди', 'звідки', 'чому', 'як', 'скільки'
        }
        
        # Слова, що позначають питання
        self.question_words = {
            'що', 'хто', 'де', 'коли', 'чому', 'як', 'чи', 'куди', 'звідки',
            'скільки', 'який', 'яка', 'яке', 'які', 'чий', 'чия', 'чиє', 'чиї',
            'якщо', 'якби', 'чи не', 'чи ж', 'чи то', 'чи може', 'чи можливо',
            'чи правда', 'чи дійсно', 'чи справді', 'чи точно', 'чи точно що'
        }
        
        # Слова, що позначають оклик
        self.exclamation_words = {
            'вау', 'о', 'ах', 'ой', 'ух', 'фух', 'боже', 'господи', 'чорт',
            'блин', 'нехай', 'хай', 'давай', 'давайте', 'стоп', 'стій',
            'зачекай', 'почекай', 'тримай', 'лови', 'біжи', 'лети',
            'ура', 'браво', 'молодець', 'чудово', 'відмінно', 'супер',
            'фантастично', 'неймовірно', 'дивовижно', 'прекрасно'
        }
        
        # Слова, що позначають завершення думки
        self.ending_words = {
            'все', 'ось і все', 'от і все', 'от так', 'ось так', 'так ось',
            'от і все тут', 'ось і все тут', 'більше нічого', 'нічого більше',
            'все це', 'це все', 'все тут', 'тут все', 'все добре', 'добре все'
        }
        
        # Патерни для розпізнавання різних типів речень
        self.sentence_patterns = {
            'question': [
                r'\b(що|хто|де|коли|чому|як|чи|куди|звідки|скільки|який|яка|яке|які|чий|чия|чиє|чиї)\b',
                r'\bчи\s+(не|ж|то|може|правда|дійсно|справді|точно)\b',
                r'\b(якщо|якби)\b',
                r'\b(можливо|може|напевно|напевне|звичайно|звісно)\s+(це|так|воно|воно)\b'
            ],
            'exclamation': [
                r'\b(вау|о|ах|ой|ух|фух|боже|господи|чорт|блин)\b',
                r'\b(ура|браво|молодець|чудово|відмінно|супер|фантастично|неймовірно|дивовижно|прекрасно)\b',
                r'\b(нехай|хай|давай|давайте)\b',
                r'\b(стоп|стій|зачекай|почекай|тримай|лови|біжи|лети)\b'
            ],
            'command': [
                r'\b(зроби|зробіть|напиши|напишіть|покажи|покажіть|дай|дайте|принеси|принесіть)\b',
                r'\b(йди|йдіть|іди|ідіть|біжи|біжіть|лети|летіть|їдь|їдьте)\b',
                r'\b(закрий|закрийте|відкрий|відкрийте|вимкни|вимкніть|увімкни|увімкніть)\b'
            ]
        }
    
    def process_text(self, text: str) -> str:
        """
        Основний метод обробки тексту з розділовими знаками
        """
        if not text or not text.strip():
            return text
        
        logger.info(f"Початок обробки тексту: {text}")
        
        # Крок 1: Базова очистка
        text = self._clean_text(text)
        
        # Крок 2: Розділення на речення
        sentences = self._split_into_sentences(text)
        
        # Крок 3: Обробка кожного речення
        processed_sentences = []
        for sentence in sentences:
            if sentence.strip():
                processed_sentence = self._process_sentence(sentence.strip())
                processed_sentences.append(processed_sentence)
        
        # Крок 4: З'єднання речень
        result = ' '.join(processed_sentences)
        
        # Крок 5: Фінальна очистка
        result = self._final_cleanup(result)
        
        logger.info(f"Результат обробки: {result}")
        return result
    
    def _clean_text(self, text: str) -> str:
        """Очищення тексту від зайвих пробілів та символів"""
        # Видаляємо зайві пробіли
        text = re.sub(r'\s+', ' ', text)
        # Видаляємо пробіли на початку та в кінці
        text = text.strip()
        # Видаляємо зайві розділові знаки
        text = re.sub(r'[.!?]+', '.', text)
        text = re.sub(r'[,;]+', ',', text)
        return text
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Розділення тексту на речення"""
        # Розділяємо за крапками, знаками оклику та питання
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _process_sentence(self, sentence: str) -> str:
        """Обробка окремого речення"""
        if not sentence:
            return sentence
        
        # Визначаємо тип речення
        sentence_type = self._determine_sentence_type(sentence)
        
        # Додаємо коми
        sentence = self._add_commas(sentence)
        
        # Додаємо кінцевий знак
        sentence = self._add_ending_punctuation(sentence, sentence_type)
        
        # Капіталізуємо першу літеру
        sentence = self._capitalize_first_letter(sentence)
        
        return sentence
    
    def _determine_sentence_type(self, sentence: str) -> str:
        """Визначення типу речення"""
        sentence_lower = sentence.lower()
        
        # Перевіряємо питання
        for pattern in self.sentence_patterns['question']:
            if re.search(pattern, sentence_lower):
                return 'question'
        
        # Перевіряємо оклик
        for pattern in self.sentence_patterns['exclamation']:
            if re.search(pattern, sentence_lower):
                return 'exclamation'
        
        # Перевіряємо команду
        for pattern in self.sentence_patterns['command']:
            if re.search(pattern, sentence_lower):
                return 'command'
        
        return 'statement'
    
    def _add_commas(self, sentence: str) -> str:
        """Додавання ком у речення"""
        words = sentence.split()
        if len(words) <= 1:
            return sentence
        
        result_words = []
        
        for i, word in enumerate(words):
            current_word = word.lower().strip('.,!?;:')
            
            # Кома після певних слів
            if current_word in self.comma_after_words:
                if not word.endswith(','):
                    result_words.append(word + ',')
                else:
                    result_words.append(word)
            
            # Кома перед сполучниками (але не перед "що" в питаннях)
            elif current_word in self.comma_before_conjunctions and i > 0:
                # Не додаємо кому перед "що" якщо це питання
                if current_word == 'що' and self._is_question_sentence(sentence):
                    result_words.append(word)
                else:
                    if not result_words[-1].endswith(','):
                        result_words[-1] = result_words[-1] + ','
                    result_words.append(word)
            
            # Кома після вступних фраз
            elif self._is_introductory_phrase(words, i):
                if not word.endswith(','):
                    result_words.append(word + ',')
                else:
                    result_words.append(word)
            
            else:
                result_words.append(word)
        
        return ' '.join(result_words)
    
    def _is_question_sentence(self, sentence: str) -> bool:
        """Перевірка чи є речення питанням"""
        sentence_lower = sentence.lower()
        
        # Перевіряємо чи починається з питального слова
        question_starters = ['що', 'хто', 'де', 'коли', 'чому', 'як', 'чи', 'куди', 'звідки', 'скільки', 'який', 'яка', 'яке', 'які']
        first_word = sentence_lower.split()[0] if sentence_lower.split() else ""
        
        if first_word in question_starters:
            return True
        
        # Перевіряємо чи містить "чи"
        if 'чи' in sentence_lower:
            return True
        
        return False
    
    def _is_introductory_phrase(self, words: List[str], index: int) -> bool:
        """Перевірка чи є слово частиною вступної фрази"""
        if index == 0:
            return False
        
        # Перевіряємо фрази з 2-3 слів
        phrases = [
            'чесно кажучи', 'правду кажучи', 'взагалі то', 'власне кажучи',
            'між іншим', 'до речі', 'до слова', 'до того ж', 'крім того',
            'більше того', 'тим більше', 'тим паче', 'на жаль', 'на щастя',
            'на диво', 'на превеликий жаль', 'коротше кажучи', 'одним словом',
            'в кінці кінців', 'в підсумку', 'виходить', 'отже', 'от і все',
            'ось і все', 'незважаючи на те що', 'попри те що', 'замість того щоб'
        ]
        
        # Перевіряємо фрази назад від поточного слова
        for phrase in phrases:
            phrase_words = phrase.split()
            if len(phrase_words) <= index + 1:
                # Перевіряємо чи починається фраза з поточного слова
                if index + len(phrase_words) <= len(words):
                    current_phrase = ' '.join(words[index:index + len(phrase_words)]).lower()
                    if current_phrase == phrase:
                        return True
        
        # Перевіряємо окремі вступні слова
        introductory_words = {
            'чесно', 'правду', 'взагалі', 'власне', 'між', 'до', 'крім', 'більше',
            'тим', 'на', 'коротше', 'одним', 'словом', 'в', 'кінці', 'підсумку',
            'виходить', 'отже', 'от', 'ось', 'незважаючи', 'попри', 'замість'
        }
        
        current_word = words[index].lower().strip('.,!?;:')
        return current_word in introductory_words
    
    def _add_ending_punctuation(self, sentence: str, sentence_type: str) -> str:
        """Додавання кінцевого знаку розділового знаку"""
        # Видаляємо існуючі кінцеві знаки
        sentence = re.sub(r'[.!?]+$', '', sentence)
        
        if sentence_type == 'question':
            return sentence + '?'
        elif sentence_type == 'exclamation':
            return sentence + '!'
        elif sentence_type == 'command':
            return sentence + '!'
        else:
            return sentence + '.'
    
    def _capitalize_first_letter(self, sentence: str) -> str:
        """Капіталізація першої літери"""
        if not sentence:
            return sentence
        
        # Знаходимо першу літеру
        for i, char in enumerate(sentence):
            if char.isalpha():
                return sentence[:i] + char.upper() + sentence[i+1:]
        
        return sentence
    
    def _final_cleanup(self, text: str) -> str:
        """Фінальна очистка тексту"""
        # Виправляємо зайві пробіли перед знаками
        text = re.sub(r'\s+([.,!?:;])', r'\1', text)
        
        # Виправляємо подвійні знаки
        text = re.sub(r'[.,!?:;]+', lambda m: m.group()[0], text)
        
        # Виправляємо пробіли після ком
        text = re.sub(r',\s*', ', ', text)
        
        # Видаляємо зайві пробіли
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

# Функція для зручного використання
def improve_ukrainian_text(text: str) -> str:
    """
    Зручна функція для покращення українського тексту з розділовими знаками
    
    Args:
        text (str): Вхідний текст без розділових знаків
        
    Returns:
        str: Текст з правильно розставленими розділовими знаками
    """
    processor = UkrainianPunctuationProcessor()
    return processor.process_text(text) 