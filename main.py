import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# whitelist пользователей
ALLOWED_USERS = {
    1718888770,
    234335061# твой Telegram ID
}

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту")
        return
    url = update.message.text

    await update.message.reply_text("Скачиваю видео...")

    ydl_opts = {
        "outtmpl": "video.mp4",
        "format": "mp4"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    await update.message.reply_video(video=open("video.mp4", "rb"))

    os.remove("video.mp4")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

app.run_polling()
