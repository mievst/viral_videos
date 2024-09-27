from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import nltk
nltk.download('punkt_tab')

class TranslatorToRussian:
    def __init__(self):
        # Загрузка модели и токенизатора для перевода с английского на русский
        self.model_name = 'facebook/nllb-200-distilled-600M'
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

        self.pipe = pipeline(
            "translation",
            model=self.model,
            tokenizer=self.tokenizer,
            src_lang="eng_Latn",
            tgt_lang="rus_Cyrl",
            device=self.device,
            torch_dtype=self.torch_dtype
            )

    def translate_to_russian(self, text):
        try:
            # Split text into sentences
            sentences = nltk.sent_tokenize(text)
            translated_sentences = []
            for sentence in sentences:
                translated_text = self.pipe(sentence)
                translated_sentences.append(translated_text[0]['translation_text'])

            # Concatenate translated sentences into text
            translated_text = ' '.join(translated_sentences)
            return translated_text
        except Exception as e:
            return f"Error: {e}"

# Пример использования
if __name__ == "__main__":
    translator = TranslatorToRussian()
    text_to_translate = "Do it! Just do it! Don't let your dreams be dreams. Yesterday you said tomorrow, so"
    translated_text = translator.translate_to_russian(text_to_translate)
    print(f"Original text: {text_to_translate}")
    print(f"Translated text: {translated_text}")