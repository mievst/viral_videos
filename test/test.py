import requests
import time
import json

BASE_URL = 'http://127.0.0.1:5000'

def upload_video(video_path):
    with open(video_path, 'rb') as video_file:
        response = requests.post(f'{BASE_URL}/upload/video', files={'video': video_file}, params={'video_duration': 30})
        print(f'Upload response: {response.status_code}, {response.text}')
        return response.json().get('id')  # Возвращает идентификатор задачи

def get_video_status(task_id):
    response = requests.get(f'{BASE_URL}/video_status', params={'task_id': task_id})
    if response.status_code == 200:
        return response.json().get('status')
    else:
        print(f'Error fetching status: {response.status_code}, {response.json()}')
        return None

def get_video_result(task_id):
    response = requests.get(f'{BASE_URL}/video_result', params={'task_id': task_id})
    if response.status_code == 200:
        result = response.json()
        print(f'Task result: {result}')
        save_result_to_file(task_id, result)
    else:
        print(f'Error fetching result: {response.status_code}, {response.json()}')

def save_result_to_file(task_id, result):
    # Сохранение результата в файл
    filename = f'task_result_{task_id}.json'
    with open(filename, 'w') as file:
        json.dump(result, file, indent=4)
    print(f'Results saved to {filename}')

def wait_for_task_completion(task_id, check_interval=5):
    while True:
        status = get_video_status(task_id)
        if status:
            print(f'Current task status: {status}')
            if status in ['SUCCESS', 'FAILED']:
                return status
        time.sleep(check_interval)  # Ждем заданный интервал перед повторной проверкой

if __name__ == "__main__":
    video_path = "C:\\Users\\mievst\\Desktop\\train_dataset_viral_videos_train\\0c6e4cdaa192d1ae58b99bc9f35891b9.mp4"

    # Загрузка видео и получение task_id
    task_id = upload_video(video_path)

    # Ожидание завершения задачи
    final_status = wait_for_task_completion(task_id)

    # Если задача завершена успешно, запрашиваем результат и сохраняем его в файл
    if final_status == 'SUCCESS':
        get_video_result(task_id)
    elif final_status == 'FAILED':
        print('Task failed.')
