import random
from moviepy.editor import VideoFileClip

class ClipDetector:
    def __init__(self, video_path):
        self.video_path = video_path
        pass

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
        timestamps = [round(random.uniform(0, duration), 2) for _ in range(2)]

        return {"timestamp": timestamps}