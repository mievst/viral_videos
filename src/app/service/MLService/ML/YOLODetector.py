from ultralytics import YOLO
import cv2

class YOLODetector:
    def __init__(self, model_name='yolov8n'):
        # Загружаем модель YOLO через ultralytics
        self.model = YOLO(model_name)
        self.tracker = None  # Для трекинга
        self.tracking_person = None  # Координаты отслеживаемого человека
        self.tracking_counter = 0  # Счётчик кадров, на которых отслеживаем человека

    def detect_person(self, frame):
        # Если активен трекинг, обновляем позицию
        if self.tracker is not None:
            success, bbox = self.tracker.update(frame)
            if success:
                self.tracking_person = bbox
                self.tracking_counter -= 1
                return bbox
            else:
                self.tracker = None
                self.tracking_person = None
                self.tracking_counter = 0

        # В противном случае запускаем YOLO для детекции
        results = self.model(frame)
        persons = []
        for result in results:
            if len(result.boxes.cls) > 0 and result.boxes.cls[0].item() == 0:  # Только человек
                x1, y1, x2, y2 = map(int, result.boxes.xyxy[0].cpu().numpy())
                persons.append((x1, y1, x2, y2))

        # Фильтрация по классу "человек" (class 0 в COCO dataset)
        #persons = [det for det in detections if int(det[-1]) == 0]

        if len(persons) == 0:
            return None

        # Если несколько людей, выбираем по трекингу или площади bounding box
        if len(persons) > 1 and self.tracking_counter <= 0:
            largest_person = self.select_person_to_track(persons)
            self.start_tracking(frame, largest_person)
            return largest_person
        elif len(persons) == 1:
            largest_person = persons[0]
            self.start_tracking(frame, largest_person)
            return largest_person

        return None

    def start_tracking(self, frame, person):
        # Запуск KCF трекера с начальным bbox
        self.tracker = cv2.TrackerKCF_create()
        bbox = (person[0], person[1], person[2] - person[0], person[3] - person[1])
        self.tracker.init(frame, bbox)
        self.tracking_person = bbox
        self.tracking_counter = 100  # Фиксируем выбор человека на 100 кадров

    def select_person_to_track(self, persons):
        # Выбор самого крупного человека для отслеживания
        return max(persons, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))

    def get_largest_person(self, persons):
        # Возвращаем самого крупного человека (если трекер не используется)
        return max(persons, key=lambda x: (x[2] - x[0]) * (x[3] - x[1])) if persons else None


    def detect_persons_in_video(self, video_path):
        """
        Детекция людей в видео.

        Args:
        video_path (str): Путь к видеофайлу.

        Returns:
        list: Список bbox для каждого кадра.
        """
        cap = cv2.VideoCapture(video_path)
        bboxes = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            bbox = self.detect_person(frame)
            if bbox is not None:
                bboxes.append(bbox)

        cap.release()
        return bboxes
