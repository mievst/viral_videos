from transformers import pipeline


class LLMClassification:
    def __init__(self):
        self.classifier = pipeline(
            "zero-shot-classification", model="cointegrated/rubert-base-cased-nli-threeway", device="auto")

    def classify_chunks(self, chunks, labels, target_duration=120.0):
        ngrams = self.create_ngrams_by_time_and_duration(chunks, target_duration=120.0)
        for ngram in ngrams:
            result = self.classifier(ngram['text'], labels)
            ngram["labels"] = result["labels"]
            ngram["scores"] = result["scores"]
        return result

    def classify(self, text, lables):
        return self.classifier(text, lables)

    def create_ngrams_by_time_and_duration(self, chunks, max_overlap=0.5, target_duration=10.0):
        ngrams = []
        i = 0

        while i < len(chunks) - 1:
            # Начальные значения для первого чанка
            current_start, current_end = chunks[i]["timestamp"]
            ngram_text = chunks[i]['text']
            ngram_start = current_start
            ngram_end = current_end
            ngram_duration = ngram_end - ngram_start

            # Объединение чанков, если они не превышают заданную длительность
            while i < len(chunks) - 1:
                next_start, next_end = chunks[i + 1]["timestamp"]
                next_duration = next_end - next_start

                # Пересечение по времени
                overlap = max(0, min(current_end, next_end) -
                              max(current_start, next_start))

                # Проверяем условие на пересечение и целевую длительность
                if overlap / min(ngram_duration, next_duration) <= max_overlap and (ngram_duration + next_duration) <= target_duration:
                    # Обновляем энграмму
                    ngram_text += " " + chunks[i + 1]['text']
                    ngram_end = next_end
                    ngram_duration = ngram_end - ngram_start
                    i += 1  # Продвигаемся к следующему чанку
                else:
                    break

            # Добавляем текущую энграмму в список
            ngrams.append(
                {"text": ngram_text, "timestamp": [ngram_start, ngram_end]})
            i += 1  # Переходим к следующему чанку

        # Обрабатываем последний чанк, если он не вошел в энграмму
        if i < len(chunks):
            ngrams.append(
                {"text": chunks[i]['text'], "timestamp": chunks[i]["timestamp"]})

        return ngrams
