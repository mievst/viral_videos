from moviepy.video.io.VideoFileClip import VideoFileClip
import os.path

class VideoCutService:

    def cut_video(self, video_path, timestamps):
        clips = []
        video = VideoFileClip(video_path)
        video_duration = video.duration
        for i, (start_time, end_time) in enumerate(timestamps):
            if start_time < 0 or end_time > video_duration or start_time >= end_time:
                continue
            clip = video.subclip(start_time, end_time)
            clips.append(clip)
        return clips

    def save_clips(self, clips, user_id):
        user_folder_path = os.path.join("videos/", user_id)
        # создать папку virals для юзера, если ее нет
        virals_folder = os.path.join(user_folder_path, 'virals')
        if not os.path.exists(virals_folder):
            os.makedirs(virals_folder)

        for i, clip in enumerate(clips):
            clip.write_videofile(f"{virals_folder}/clip_{i + 1}.mp4", codec="libx264")


