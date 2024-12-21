from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram import F
import re, os, uuid, logging, asyncio, json, yt_dlp, subprocess, threading, requests

from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

from config import *
from gpt import answer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def startTor():
    subprocess.run([os.path.join(os.getcwd(), "TorBrowser", "Tor", "tor.exe"), "-f", os.path.join(os.getcwd(), "TorBrowser", "Data", "Tor", "torrc")], check=True)

def is_tor_connected():
    try:
        response = requests.get("https://check.torproject.org", proxies={"http": "socks5h://127.0.0.1:9060", "https": "socks5h://127.0.0.1:9060"})
        return "Congratulations" in response.text
    except requests.RequestException:
        return False

def youtubeDownloader(url):
    fileName = str(uuid.uuid4())
    ydl_opts["outtmpl"] = fileName
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return fileName+".mp3"

@dp.message(F.text)
async def process_message(message: Message):
    text = message.text.strip()

    if re.match(YOUTUBE_URL_PATTERN, text):
        sent_message = await message.reply(f"Обрабатывается видео: {text}")
        try:
            fileName = youtubeDownloader(text.split("&")[0])
            mp3 = AudioSegment.from_mp3(fileName)
            mp3 = mp3.set_channels(CHANNELS)
            mp3 = mp3.set_frame_rate(FRAME_RATE)
            rec = KaldiRecognizer(model, FRAME_RATE)
            rec.SetWords(True)

            rec.AcceptWaveform(mp3.raw_data)
            result = rec.Result()
            recText = json.loads(result)["text"]
            msg = f"Распознан текст: {recText}"
            await bot.delete_message(sent_message.chat.id, sent_message.message_id)
            for i in range(0, len(msg), MAX_MESSAGE_LENGTH):
                await bot.send_message(sent_message.chat.id, msg[i:i+MAX_MESSAGE_LENGTH])
            gptText = answer(
                    prompt = 'Представь, что ты — эксперт по анализу контента. Я передам тебе текстовую расшифровку видеоролика. Твоя задача — кратко изложить основную идею и ключевые моменты в одном-двух абзацах. Укажи, о чём видео и основные тезисы. Максимальная длинна ответа: 1500 символов',
                    text = f"Текст: {recText}",
                    limit = 5,
                )
            os.remove(fileName)
            await bot.send_message(
                    text=f"Ответ GPT по видео: {gptText}",
                    chat_id=sent_message.chat.id,
                )
        except Exception as e:
            logger.error(e)
            await bot.send_message(
                    text=f"Возникла ошибка при распознавании текста",
                    chat_id=sent_message.chat.id
                )
    else:
        await message.reply("Пожалуйста, отправьте корректную ссылку от YouTube.")

async def main():
    global model
    logger.info("Loading model")
    model = Model("model")
    logger.info("Loading TOR network")
    torThread = threading.Thread(target=startTor)
    torThread.start()
    while not is_tor_connected():
        is_tor_connected()
    logger.info("Tor is fully connected!")
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
