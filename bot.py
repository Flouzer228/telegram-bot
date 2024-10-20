from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram import ChatPermissions
from datetime import datetime, timedelta
import logging
import asyncio
import nest_asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '7610569202:AAGzq4Zv2zqJiuyOIAF4Mlanlxksy4b4KKM'

mute_times = {}

def contains_profanity(message: str) -> bool:
    profanity_list = ["сука", "блять", "пиздец", "нахуя", "еблан", "уебище", "гандон", "тварь", "скатина", "даун", "гнида", "ущерб", "пизда", "хуй", "член", "вагина", "блядина", "доебался", "ебало", "ебанешься", "ебанулся", "ебашит", "заебись", "ахуенно", "спиздил", "пиздабол", "пиздатый", "хуйня"]
    return any(word in message.lower() for word in profanity_list)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    current_time = datetime.now()

    # Проверяем, нужно ли снять мут
    if user_id in mute_times:
        if current_time > mute_times[user_id]:
            del mute_times[user_id]
        else:
            await update.message.reply_text("Вы уже в муте.")
            return  # Прекращаем обработку, если пользователь в муте

    # Проверяем на нецензурную лексику
    if contains_profanity(update.message.text):
        logger.info("Profanity detected from user: %s", user_id)
        await update.message.delete()  # Удаляем сообщение
        mute_times[user_id] = current_time + timedelta(seconds=3600)  # 1 час
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=mute_times[user_id]
        )
        await update.message.reply_text("Вы получили мут на 1 час.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.run_polling()
    await app.shutdown()

if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
