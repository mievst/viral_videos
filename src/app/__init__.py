from flask import Flask
from flask_session import Session

from app.service.MLService.ClipDetector import ClipDetector
from app.service.VideoCutService import VideoCutService
from app.service.VideoUploadService import VideoUploadService

from app.constants.constants import Constants

app = Flask(__name__)
app.config.from_object('app.config.Config')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config[Constants.video_service_key] = VideoUploadService()
#app.config[Constants.ml_service_key] = ClipDetector()
#app.config[Constants.video_cut_service_key] = VideoCutService()

Session(app)

from app import routes