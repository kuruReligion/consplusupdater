import os
import requests
import subprocess
import time
from tqdm import tqdm
import shutil
import tempfile

url = 'http://www.urspectr.info/upload.php'
send_folder = 'SEND'
downloads_folder = 'downloads'
receive_folder = 'Receive'
sevenz_path = '7z.exe'


def upload(url, folder_path):
    files = os.listdir(folder_path)
    data = {'action': 'upload', 'comment': 'QST file'}
    print('Загружаю QST файлы...')
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'rb') as file:
            files = {'filenew': (file_name, file)}
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                print(f'Файл {file_name} успешно загружен!')
            else:
                print(f'Произошла ошибка при загрузке файла {file_name}.')


def download(send_folder):
    # Получаем список файлов в папке SEND
    files_to_download = os.listdir(send_folder)

    # Преобразуем имена файлов в соответствующие ссылки
    download_links = {}
    for file_name in files_to_download:
        if file_name.endswith('.QST'):
            # Извлекаем фразы из имени файла
            phrases = file_name[:-4].split('#')
            if len(phrases) == 2:
                file_base_name = phrases[0]
                file_extension = phrases[1]
                # Строим ссылку на скачивание
                download_link = f'http://www.urspectr.info/downloads/{file_base_name}!{file_extension}.EXE'
                download_links[file_name] = download_link

    print('Начинаю скачивать файлы...')
    for file_name, download_link in download_links.items():
        response = requests.get(download_link, stream=True)
        while response.status_code != 200:
            print(f'{file_name[:-4]}.EXE еще не готов для скачивания. Ждем 30 сек.')
            time.sleep(30)

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 КБ
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=file_name[:-4])

        with open(os.path.join(downloads_folder, f'{file_name[:-4]}.EXE'), 'wb') as f:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()
        print(f'{file_name[:-4]}.EXE успешно скачан!')

    print('Все файлы успешно скачаны!')


def unpack(folder_path):
    files_to_unpack = os.listdir(folder_path)
    # Фильтруем только exe файлы
    exe_files = [file for file in files_to_unpack if file.endswith('.EXE')]

    print('Распаковываю архивы...')
    for exe_file in exe_files:
        exe_path = os.path.join(folder_path, exe_file)
        # Выполняем команду для распаковки с помощью 7z
        subprocess.run([sevenz_path, 'x', '-y', exe_path, f'-o{receive_folder}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print('Распаковка завершена.')


def clear_and_create_folders():
    for folder in [receive_folder, downloads_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)


def check_send_folder():
    if not os.path.exists(send_folder):
        os.makedirs(send_folder)
        print(f"Папка {send_folder} создана.")
        input(f"Поместите файлы в папку {send_folder} и нажмите Enter...")
    else:
        print(f"Папка {send_folder} найдена")


if __name__ == '__main__':
    try:

        print('Для ручного обновления КонсультантПлюс необходимо:\n'
              '1. В КонсультантПлюс перейти в Сервис -> Сформировать запрос по ИБ -> ОК\n'
              '2. Скопировать папку SEND из расположения ConsPlusBel и положить ее в ту же директорию, в которой находится эта программа\n\n'
              'Программа загрузит файлы из папки SEND на сервер ЮрСпектра, а затем скачает и распакует необходимые файлы.\n'
              'Это может занять много времени.\n\n'
              'Убедитесь, что на компьютере есть интернет и файл 7z.exe находится рядом с программой!\n')
        input("3. Для продолжения нажмите Enter...")
        print('\n')

        temp_dir = tempfile.mkdtemp()
        shutil.copy('7z.exe', temp_dir)

        check_send_folder()
        clear_and_create_folders()
        upload(url, send_folder)
        download(send_folder)
        unpack(downloads_folder)
        print('Успех! Папка Receive готова!\n\n'
              '4. Переместить файлы из папки Receive в папку RECEIVE в расположении ConsPlusBel\n'
              '5. В КонсультантПлюс перейти в Сервис -> Операции с Информационным банком\n'
              '6. Отметить "Пополнение из дериктории RECEIVE", нажать "Выполнить"\n\n')
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    input("Нажмите Enter для выхода...")
