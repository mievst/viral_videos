from moviepy.video.io.VideoFileClip import VideoFileClip
import os.path
import cv2
import numpy as np
import subprocess
from .MLService.ML.YOLODetector import YOLODetector

class VideoCutService:
    def __init__(self, input_video_path, temp_video_path, aspect_ratio=(9, 16)):
        self.input_video_path = input_video_path
        self.temp_video_path = temp_video_path
        self.aspect_ratio = aspect_ratio
        self.user_folder_path = None
        self.yolo = YOLODetector()

    def cut_video(self, video_path, clip_data, user_id):
        clips = []
        with VideoFileClip(video_path) as video:
            video_duration = video.duration
            fps = video.fps
            self.user_folder_path = os.path.join("videos/", user_id)
            virals_folder = os.path.join(self.user_folder_path, 'virals')
            if not os.path.exists(virals_folder):
                os.makedirs(virals_folder)
            for i, data in enumerate(clip_data):
                start_time, end_time = data["timestamp"]
                if start_time < 0 or end_time > video_duration or start_time >= end_time:
                    continue
                clip = video.subclip(start_time, end_time)
                clip_path = f"{virals_folder}/clip_{i + 1}.mp4"
                clip.write_videofile(clip_path, codec="libx264", fps=fps)
                clips.append(clip_path)
        return clips

    def process_video(self, clips):
        processed_clips = []
        prev_bbox = None
        for i, clip_path in enumerate(clips):
            cropped_folder = os.path.join(self.user_folder_path, 'cropped')
            audio_folder = os.path.join(self.user_folder_path, 'audio')
            temp_video_path = f"{cropped_folder}_{i}.mp4"
            audio_video_path = f"{audio_folder}_{i}.mp3"
            cap = cv2.VideoCapture(clip_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            aspect_ratio = self.aspect_ratio[0] / self.aspect_ratio[1]
            out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                bbox = self.yolo.detect_person(frame)
                if bbox is not None:
                    prev_bbox = bbox
                else:
                    bbox = prev_bbox
                x1, y1, x2, y2 = bbox
                x_center = int((x1 + x2) / 2)
                y_center = int((y1 + y2) / 2)

                new_width = height * aspect_ratio
                crop_x1 = max(0, x_center - new_width // 2)
                crop_x2 = min(width, x_center + new_width // 2)

                cropped_frame = frame[:, int(crop_x1):int(crop_x2)]
                resized_frame = cv2.resize(cropped_frame, (width, height))

                out.write(resized_frame)
            processed_clips.append((audio_video_path, bbox))

            cap.release()
            out.release()
            cv2.destroyAllWindows()

            self.add_audio_to_video(clip_path, temp_video_path, audio_video_path)
            return processed_clips

    def add_audio_to_video(self, original_clip_path, temp_clip_path, new_clip_path):
        command = f"ffmpeg -i {temp_clip_path} -i {original_clip_path} -c copy -map 0:v -map 1:a -y {new_clip_path}"
        os.system(command)

    def run(self, clip_data, user_id):
        clips = self.cut_video(self.input_video_path, clip_data, user_id)
        #processed_clips = self.process_video(clips)
        #for i, clip_path in enumerate(clips):
            #os.replace(clip_path, processed_clips[i][0])
