import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from moviepy.editor import AudioFileClip

class SpeechRecognition:
    def __init__(self, model_id="openai/whisper-large-v3"):
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            return_timestamps=True,
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
            chunk_length_s=30
        )

    def recognize_speech(self, audio_file):
        result = self.pipe(audio_file)

        if len(result["chunks"]) > 0:
            audio_duration = self.get_audio_duration(audio_file)
            result["chunks"][-1]["timestamp"] = (result["chunks"][-1]["timestamp"][0], audio_duration)
        return result

    def get_audio_duration(self, audio_file):
        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration
        return duration


# Пример использования класса
if __name__ == "__main__":
    import json
    speech_recognizer = SpeechRecognition()
    result = speech_recognizer.recognize_speech("./experiments/audio.wav")
    with open("./experiments/result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    print(result["chunks"][0:30])