import random
import torch
from transformers import pipeline
from moviepy.editor import VideoFileClip
from src.ML.stt import SpeechRecognition
from src.ML.LLMClassification import LLMClassification
import os

class ClipDetector:
    def __init__(self, video_path, temp_dir):
        self.video_path = video_path
        self.temp_dir = temp_dir
        self.stt = SpeechRecognition()
        self.llm = LLMClassification()
        self.chunks = None

        self.viral_lables = ["юмор", "шок", "негатив", "удивление"]
        self.tags = [
            "влог", "обучение", "юмор", "рецепт", "спорт", "мотивация", "DIY", "путешествия",
            "семья", "дети", "знаменитости", "интервью", "искусство", "фитнес", "лайфхаки",
            "мода", "стиль", "макияж", "уроки", "гаджеты", "технологии", "анбоксинг", "летсплей",
            "игры", "киберспорт", "анимация", "компьютерная графика", "3D-моделирование",
            "музыка", "танцы", "комедия", "пранки", "эксперименты", "челлендж", "вопросы и ответы",
            "блоггинг", "подкаст", "реакция", "обзор фильмов", "обзор сериалов", "обзор книг",
            "обзор игр", "наука", "технологические обзоры", "мобильные телефоны", "обзоры приложений",
            "забавные видео", "животные", "кошки", "собаки", "зоопарк", "природа", "документальный фильм",
            "автомобили", "гонки", "хобби", "фотография", "видеосъемка", "рекламные ролики", "инфлюенсеры",
            "личный рост", "здоровье", "психология", "питание", "креатив", "мультфильмы", "ностальгия",
            "история", "культура", "социальные темы", "образование", "жизненные истории", "документалистика",
            "новости", "политика", "тренды", "анализ", "прогнозы", "инструкции", "ремонт", "строительство",
            "экология", "инвестиции", "финансы", "экономика", "маркетинг", "программирование", "машинное обучение",
            "робототехника", "искусственный интеллект", "UX/UI дизайн", "стартапы", "предпринимательство",
            "геймеры", "летсплейщики", "космос", "астрономия", "фантастика", "творчество", "поэзия",
            "литература", "интернет-тренды", "мемы"
        ]

    def detect(self, target_duration=120.0):
        """
        Основная функция для обнаружения кадров
        """
        self.__create_transcribtion()
        result = self.llm.classify_chunks(self.chunks, self.viral_lables, target_duration)
        top_results = sorted(result, key=lambda x: max(x['scores']), reverse=True)
        if len(top_results) > 20:
            top_results = top_results[:20]
        return top_results

    def __create_transcribtion(self):
        video = VideoFileClip(self.video_path)
        video_name = os.path.basename(self.video_path).split(".")[0]
        audio_path = os.path.join(self.temp_dir, f"{video_name}.wav"
        video.audio.write_audiofile(audio_path)
        self.chunks = stt.recognize_speech(audio_path)

    def get_tags(self, texts):
        results = []
        for text in texts:
            result = self.llm.classify(text, self.viral_lables)
            results.append(result)
        return results

    def mock_detect(self):
        """
        Заглушка для детекции. Возвращает массив рандомных временных меток, ограниченных по диапазону длительностью видео.

        :param video_path: Путь к видеофайлу
        :return: Массив рандомных временных меток
        """
        # Загружаем видео и получаем его длительность
        video = VideoFileClip(self.video_path)
        duration = video.duration

        # Генерируем рандомные временные метки в диапазоне от 0 до длительности видео
        timestamps = []
        for _ in range(20):
            num1 = random.uniform(0, duration)
            num2 = random.uniform(num1, duration)
            timestamps.append((num1, num2))

        return timestamps