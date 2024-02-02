# О программе
Небольшой помощник для ручного обновления КонсультантПлюс<br>
<b><a href='https://drive.google.com/file/d/1jG-GfgnK57IpO8w-i6MO2axT9PuYbNK0/view?usp=sharing'>Скачать .exe с Гугл Диска</a></b>


# Скриншот
<img width="1280" alt="Снимок экрана 2024-02-02 172422" src="https://github.com/kuruReligion/consplusupdater/assets/77706298/f28eea9a-1f36-4cb7-a8cf-6e7323d74263">

# Как развернуть проект на своем компьютере и собрать свой .exe-файл?
python -m venv venv<br>
.\venv\Scripts\Activate.ps1<br>
pip install -r requirements.txt<br>
pyinstaller --onefile main.py
