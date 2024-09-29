import os.path
import gradio as gr
import threading

from flask import session, jsonify, request, render_template, redirect
from app.constants.constants import Constants
from app import app
import uuid
from .service.MLService.ClipDetector import ClipDetector
from app.service.VideoCutService import VideoCutService


tasks = {}

def running_task(task_id):
    try:
        tasks[task_id]['status'] = 'PROCESS'
        video_duration = tasks[task_id]["video_duration"]

        # отправка запроса к сервису
        # поля:
        # video_path
        # video_duration
        # video_keywords
        user_id = task_id
        user_folder_path = os.path.join("src/videos/", user_id)

        files = os.listdir(user_folder_path)
        filtered_files = [f for f in files if not os.path.isdir(
            os.path.join(user_folder_path, f))]
        file = filtered_files[0]

        video_path = os.path.join(user_folder_path, file)
        ml_service = ClipDetector(video_path, "./src/app/temp")
        # response = ml_service.mock_detect()
        response = ml_service.detect(video_duration)
        # timestamps должны браться из response
        # нарезка файлов
        # файлы сохраняются в videos/user_id/virals
        #video_cut_service = VideoCutService(video_path, "./src/app/temp")
        #clips = video_cut_service.run(response, user_id)
        tasks[task_id]['result'] = jsonify(response)
        tasks[task_id]['status'] = 'SUCCESS'
    except Exception as e:
        tasks[task_id]['status'] = 'FAILED'
        tasks[task_id]['result'] = str(e)

@app.before_request
def before_request():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())


@app.route('/')
def index():
    pass

#  загрузить одно видео


@app.route('/upload/video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "No video part in request", 400

    file = request.files['video']

    if file.filename == '':
        return 'No selected video', 400

    if file:
        video_duration = request.form.get('video_duration')
        service = app.config[Constants.video_service_key]
        response = service.upload_video(session[Constants.user_id], file)
        tasks[Constants.user_id] = {'id': Constants.user_id, 'status': 'CREATED', 'video_duration': video_duration, 'result': None}
        thread = threading.Thread(target=running_task, args=(Constants.user_id,))
        thread.start()
        if response != '':
            return response, 200


# получить видео с сервера
@app.route('/get/uploaded/video', methods=['GET'])
def get_uploaded_video():
    pass

# получить виральные клипы


@app.route('/video_status', methods=['GET'])
def task_status():
    task_id = request.args.get('task_id')
    task = tasks.get(task_id)
    if task:
        return jsonify({'id': task_id, 'status': task['status']})
    else:
        return jsonify({'error': 'Task not found'}), 404

@app.route('/video_result', methods=['GET'])
def task_result():
    task_id = request.args.get('task_id')
    task = tasks.get(task_id)
    if task:
        return task['result']
    else:
        return jsonify({'error': 'Task not found'}), 404
