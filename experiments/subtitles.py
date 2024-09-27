import os
import json
from tqdm import tqdm
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from ML.stt import SpeechRecognition
from ML.translator import TranslatorToRussian


class VideoSubtitler:
    def __init__(self, video_path, audio_path, chunk_duration=200):
        self.video_path = video_path
        self.audio_path = audio_path
        self.chunk_duration = chunk_duration
        self.translator = TranslatorToRussian()
        self.stt = SpeechRecognition()

        self.video = VideoFileClip(self.video_path)
        self.video_duration = self.video.duration
        self.subtitles = None

    def create_subtitle(self, output_dir, output_file, translate_to_rus=True):
        os.makedirs(output_dir, exist_ok=True)

        # Разбиение видео на чанки
        chunks = [(i, min(i + self.chunk_duration, self.video_duration))
                for i in range(0, int(self.video_duration), self.chunk_duration)]
        print(f"Количество чанков: {len(chunks)}")

        # Загрузка данных из кэша
        cache_file = os.path.join(output_dir, "cache.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                processed_chunks = json.load(f)
        else:
            processed_chunks = {}

        for i in tqdm(range(len(chunks)), desc="Processing video chunks"):
            start, end = chunks[i]

            # Пропустить уже обработанные чанки
            if str(i) in processed_chunks:
                # Обновить start следующего чанка, если текущий чанк менял тайминг
                if "end" in processed_chunks[str(i)]:
                    next_start = processed_chunks[str(i)]["end"]
                    if i + 1 < len(chunks):
                        chunks[i+1] = (next_start, chunks[i+1][1])
                continue

            # Нарезка аудио и видео через os.system
            audio_chunk_path = os.path.join(output_dir, f"audio_chunk_{i}.wav")
            os.system(f"ffmpeg -i {self.audio_path} -ss {start} -to {end} -vn -acodec pcm_s16le {audio_chunk_path} -y")

            # Распознавание речи
            stt_data = self.stt.recognize_speech(audio_chunk_path)
            subtitles_for_chunk = stt_data["chunks"]

            if len(chunks) > i + 1:
                end = subtitles_for_chunk[-2]["timestamp"][1] + start
                chunks[i] = (start, end)
                chunks[i+1] = (end, chunks[i+1][1])
                subtitles_for_chunk = subtitles_for_chunk[:-1]

            # Перевод субтитров и создание текстовых клипов
            text_clips = []
            clip = self.video.subclip(start, end)
            fontsize = int(min(clip.size) * 0.03)

            for subtitle in tqdm(subtitles_for_chunk, desc="Processing subtitles"):
                text = subtitle["text"]
                if translate_to_rus:
                    text = self.translator.translate_to_russian(text)
                text_clip = TextClip(txt=text,
                                    fontsize=fontsize,
                                    bg_color="black",
                                    size=(int(clip.w * 0.9), None),
                                    color='white',
                                    stroke_width=3,
                                    method='caption').set_position(("center", 0.8), relative=True)\
                    .set_start(subtitle["timestamp"][0])\
                    .set_duration(subtitle["timestamp"][1] - subtitle["timestamp"][0])
                text_clips.append(text_clip)

            # Композиция видео с субтитрами
            final_clip = CompositeVideoClip([clip] + text_clips)
            video_chunk_path = os.path.join(output_dir, f"chunk_video_{i}.mp4")
            final_clip.write_videofile(video_chunk_path, codec="libx264", audio=True)

            # Слияние видео и аудио чанков через os.system
            chunk_path = os.path.join(output_dir, f"chunk_{i}.mp4")
            os.system(f"ffmpeg -i {video_chunk_path} -i {audio_chunk_path} -c:v copy -c:a aac -strict experimental {chunk_path} -y")

            # Сохранение данных в кэше
            processed_chunks[str(i)] = {
                "start": start,
                "end": end,
                "subtitles": subtitles_for_chunk
            }
            with open(cache_file, "w") as f:
                json.dump(processed_chunks, f, indent=4)

            os.system(f"rm {video_chunk_path}")
            os.system(f"rm {audio_chunk_path}")

        # Объединение частей в одно видео
        self.merge_chunks(output_dir, output_file)

    def merge_chunks(self, output_dir, output_file):
        chunk_files = [os.path.join(output_dir, f) for f in sorted(
            os.listdir(output_dir)) if f.startswith("chunk_") and f.endswith("mp4")]
        concat_file = os.path.join(output_dir, "concat_list.txt")

        with open(concat_file, "w") as f:
            for chunk in chunk_files:
                f.write(f"file '{chunk}'\n")

        os.system(f"ffmpeg -f concat -safe 0 -i {concat_file} -c copy {output_file} -y")


# Пример использования класса
if __name__ == "__main__":
    high_res_video = "./viral_videos_train_2/0cf954675163c4fe8f1313b6e6bb8c19.mp4"
    video_with_audio = "./viral_videos_train_2/0cf954675163c4fe8f1313b6e6bb8c19.mp4"
    output_video_name = "./experiments/results.mp4"
    temp_dir = "./experiments/tmp"

    # Получаем аудиофайл из видео через os.system
    os.system(f"ffmpeg -i {video_with_audio} -q:a 0 -map a audio.wav -y")

    video_subtitler = VideoSubtitler(high_res_video, "audio.wav")
    video_subtitler.create_subtitle(temp_dir, output_video_name, False)
