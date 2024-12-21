from vosk import SetLogLevel
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
# SetLogLevel(0)

ydl_opts = {
    'format': 'bestaudio/best',  # Скачивание только аудио
    'outtmpl': 'audio.%(ext)s',  # Название выходного файла
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',  # Извлечение аудио с помощью ffmpeg
        'preferredcodec': 'mp3',      # Конвертация в MP3
        'preferredquality': '192',    # Качество 192 kbps
    }],
    'proxy': 'socks5://127.0.0.1:9060',
    'cookies': "data/cookies.txt"
}

FRAME_RATE = 16000

CHANNELS=1

YOUTUBE_URL_PATTERN = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"

MAX_MESSAGE_LENGTH = 4096