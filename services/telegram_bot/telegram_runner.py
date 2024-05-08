from telegram import Bot
from telegram.error import TelegramError
import sqlite3
import time
import os
import configparser
import asyncio

# Configuration
# Path to the config file (one level up from the script)
config_file_path = os.path.join(os.path.dirname(__file__), '../..', 'credentials_config.ini')
db_file_path = os.path.join(os.path.dirname(__file__), '../..', 'app_front_flask', 'db.sqlite')
# Read the config.ini file
config = configparser.ConfigParser()
config.read(config_file_path)

# Access the API key
TELEGRAM_BOT_TOKEN = config.get('telegram', 'api_key')
TELEGRAM_CHAT_ID = config.get('telegram_chat_id', 'telegram_chat_id_user1')
DB_PATH = db_file_path

# Initialize the bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)  # Use await for async call
    except TelegramError as e:
        print(f"Error sending message: {e}")



def check_for_new_messages(last_checked_id):
    new_last_id = last_checked_id
    new_messages = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, text FROM message WHERE id > ?", (last_checked_id,))
    rows = cursor.fetchall()
    for row in rows:
        new_last_id = max(new_last_id, row[0])
        new_messages.append(row[1])
    conn.close()
    return new_last_id, new_messages


async def main():
    last_checked_id = 0
    while True:
        last_checked_id, new_messages = check_for_new_messages(last_checked_id)
        if new_messages:
            for message in new_messages:
                await send_telegram_message(f"Unread message: {message}")  # Await the async function
        await asyncio.sleep(10)  # Use asyncio.sleep for async sleep



if __name__ == "__main__":
    asyncio.run(main())
