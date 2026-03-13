import os
import yt_dlp
import ffmpeg
from shazamio import Shazam

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# whitelist пользователей
ALLOWED_USERS = {
    1718888770,
    6350032264,
    234335061
}

# -------- СКАЧИВАНИЕ ВИДЕО --------

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ У тебя нет доступа")
        return

    url = update.message.text

    await update.message.reply_text("📥 Скачиваю видео...")

    ydl_opts = {
        "outtmpl": "video.mp4",
        "format": "mp4"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    await update.message.reply_video(video=open("video.mp4", "rb"))

    # извлекаем аудио
    (
        ffmpeg
        .input("video.mp4")
        .output("audio.mp3")
        .run()
    )

    # ищем музыку
    result = await recognize_music("audio.mp3")

    await update.message.reply_text(result)

    os.remove("video.mp4")
    os.remove("audio.mp3")


# -------- РАСПОЗНАВАНИЕ МУЗЫКИ --------

async def recognize_music(file_path):

    shazam = Shazam()

    out = await shazam.recognize(file_path)

    if "track" in out:
        title = out["track"]["title"]
        artist = out["track"]["subtitle"]
        return f"🎵 {artist} - {title}"

    return "❌ Музыка не найдена"


# -------- ОБРАБОТКА ВИДЕО --------

async def recognize(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if user_id not in ALLOWED_USERS:
        return

    video = update.message.video

    file = await video.get_file()
    await file.download_to_drive("video.mp4")

    (
        ffmpeg
        .input("video.mp4")
        .output("audio.mp3")
        .run()
    )

    result = await recognize_music("audio.mp3")

    await update.message.reply_text(result)


# -------- ЗАПУСК БОТА --------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.add_handler(MessageHandler(filters.VIDEO, recognize))

app.run_polling()
