import schedule
import time
from datetime import datetime
from telegram import Bot, Update
import logging
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = ''


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def get_chat_id(update: Update):
    # Extract chat ID from the update
    chat_id = update.message.chat_id
    print("Received message from chat ID:", chat_id)
    return chat_id


def send_push_message():
    bot = Bot(token=bot_token)
    chat_id = get_chat_id()
    message = "Good morning! It's 9 am. Time to start your day!"
    bot.send_message(chat_id=chat_id, text=message)


if __name__ == '__main__':
    # Schedule the message to be sent every day at 9 am
    schedule.every().day.at("16:40").do(send_push_message)

    # Keep the script running
    while True:
        schedule.run_pending()
        # time.sleep(1)
