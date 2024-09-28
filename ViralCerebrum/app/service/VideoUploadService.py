import os

class VideoUploadService:
    videos_folder = r'videos/'

    def upload_video(self, user_id, file):
        # создать папку для юзера, если ее нет
        user_folder = os.path.join(self.videos_folder, user_id)
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # сохранить туда видео
        filename = file.filename
        video_path = os.path.join(user_folder, filename)
        if os.path.exists(video_path):
            os.remove(video_path)

        print(user_folder, filename)
        file.save(video_path)
        return video_path
