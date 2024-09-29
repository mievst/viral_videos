import time
import json
import gradio as gr
import requests

typeVideo = ["Тип 1", "Тип 2", "Тип 3"]

def btn_get_viral_videos_click_handler(length, video_type, subtitles):
    print(length, video_type, subtitles)
    # запрос на сервер для получения виральных видео
    # возвращает виральные видео
    # отрисовка динамического контента
    # профит

def getclips():
    time.sleep(2)
    json_data = r'''
    [
      {
        "path": "C:\\Users\\ANDREY\\PycharmProjects\\ViralGradio\\videos\\1.mkv",
        "info": {
          "label": "Юмор",
          "transcription": "Чета как-то так"
        }
      },
      {
        "path": "C:\\Users\\ANDREY\\PycharmProjects\\ViralGradio\\videos\\2.mkv",
        "info": {
          "label": "Гнев",
          "transcription": "Чета как-то вот так"
        }
      }
    ]
    '''
    return json_data


def create_interface():
    with gr.Blocks() as demo:
        with gr.Row() as row:
            with gr.Column() as col:
                clips_length_input = gr.Textbox(label="Длина получаемых клипов")
                video_type_input = gr.Dropdown(typeVideo, label="Тип видеоконтента")
                subtitles_input = gr.Checkbox(label="Субтитры")
            with gr.Column() as col:
                output = gr.Video(height=600, show_download_button=True, elem_id="1234")
                print(output)
        with gr.Row() as row:
            # clipsinfo = gr.Textbox(visible=False)
            button = gr.Button(value="Создание клипов")
            button.click(fn=btn_get_viral_videos_click_handler, inputs=[clips_length_input,video_type_input,subtitles_input], outputs=[])

        # @gr.render(inputs=[clipsinfo], triggers=[clipsinfo.change])
        # def add_block(json1):
        #     # отправка запроса на сервер
        #     # получение данных
        #     data = json.loads(json1)
        #     for item in data:
        #         with gr.Accordion(label=item['info']['label'], open=False) as accordion:
        #             with gr.Blocks() as block:
        #                 with gr.Row():
        #                     video_path = item['path']
        #                     format = video_path.split('.')[1]
        #                     ref_video = gr.PlayableVideo(video_path, format=format, height=800, width=450)
        #                     with gr.Column():
        #                         text = gr.TextArea(value="kekekekekekekekkeekekekekekekek", label="Транскрибация")
        #                         text2 = gr.TextArea(value="типа теги", label="Теги")


    return demo
