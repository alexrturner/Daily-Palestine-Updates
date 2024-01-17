# This script is used to create markdown files and QR codes from messages sent to the Telegram bot @DailyUpdatesPalestineBot from @ltpdailyupdates

import os
import re
from datetime import datetime

import markdown
import qrcode
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, ContextTypes,
                          Filters, MessageHandler, Updater)

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# directory to save markdown files and QR codes
SAVE_DIR = 'telegram_data'
try:
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
except Exception as e:
    print(f"Error creating directory: {e}")
    
# generate QR code
def create_qr_code(username):
    qr_dir = 'QR_codes'
    qr_file_path = f'{qr_dir}/{username}.png'
    
    try:
        # ensure QR_codes directory exists
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)

        # check if QR code already exists
        if not os.path.isfile(qr_file_path):
            url = f'https://www.instagram.com/{username}/'
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            img.save(qr_file_path)
            print(f"Created QR code for {username}")
        else:
            print(f"QR code already exists for {username}")
    except Exception as e:
        print(f"Error creating QR code for {username}: {e}")


# handle new messages
def handle_message(update, context):
    if update.message and update.message.text:
        message = update.message.text
        file_name = f'{SAVE_DIR}/post_{update.message.message_id}.md'
        
        # create MD file
        with open(file_name, 'w') as file:
            file.write(markdown.markdown(message))

        # check for tagged IG handles and generate QR codes
        usernames = re.findall(r'@([a-zA-Z0-9_.]{1,30})', message)
        for username in usernames:
            create_qr_code(username)


# start the bot
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
