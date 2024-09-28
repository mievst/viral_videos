import os.path

from flask import session, jsonify, request,render_template
from app.constants.constants import Constants
from app import app
import uuid
from .service.MLService.ClipDetector import ClipDetector
from app.service.VideoCutService import VideoCutService

@app.before_request
def before_request():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

@app.route('/')
def index():
    user_id = session['user_id']
    #return f'Ваш уникальный идентификатор: {user_id}'
    return render_template(rf'test.html')

#  загрузить одно видео
@app.route('/upload/video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "No video part in request",400

    file = request.files['video']

    if file.filename == '':
        return 'No selected video',400

    if file:
        service = app.config[Constants.video_service_key]
        response = service.upload_video(session[Constants.user_id], file)
        if response != '':
            return response,200


# получить видео с сервера
@app.route('/get/uploaded/video', methods=['GET'])
def get_uploaded_video():
    pass

# получить виральные клипы
@app.route('/get/viral', methods=['GET'])
def get_viral():
    video_duration = request.args.get(Constants.video_duration)
    video_keywords = request.args.get(Constants.video_keywords)

    # отправка запроса к сервису
    # поля:
    # video_path
    # video_duration
    # video_keywords
    #user_id = session['user_id']

    user_id = 'd801f520-4168-4cdf-9f0a-a3e4624d82a0'
    user_folder_path = os.path.join("src/videos/",user_id)

    files = os.listdir(user_folder_path)
    filtered_files = [f for f in files if not os.path.isdir(os.path.join(user_folder_path, f))]
    file = filtered_files[0]

    video_path = os.path.join(user_folder_path, file)
    ml_service = ClipDetector(video_path, "./src/app/temp")
    #response = ml_service.mock_detect()
    response = ml_service.detect(30)
    # timestamps должны браться из response
    # нарезка файлов
    # файлы сохраняются в videos/user_id/virals
    video_cut_service = VideoCutService(video_path, "./src/app/temp" )
    clips = video_cut_service.run(response, user_id)
    #video_cut_service.save_clips(clips, user_id)
    return jsonify(response)
