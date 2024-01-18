# This script is used to create markdown files and QR codes from messages sent to the Telegram bot @DailyUpdatesPalestineBot from @ltpdailyupdates

import hashlib
import os
import re
import threading
import webbrowser
from datetime import datetime, timedelta

import markdown
import pytz
import qrcode
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, ContextTypes,
                          Filters, MessageHandler, Updater)

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

def create_directories(base_dir='message_data'):
    markdown_dir = os.path.join(base_dir, 'markdown')
    html_dir = os.path.join(base_dir, 'html')
    qr_code_dir = os.path.join(base_dir, 'qr_codes')

    os.makedirs(markdown_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(qr_code_dir, exist_ok=True)

    return markdown_dir, html_dir, qr_code_dir

MARKDOWN_DIR, HTML_DIR, QR_DIR = create_directories()

def create_qr_code_ig(username):
    qr_file_path = f'{QR_DIR}/{username}.png'
    try:
        # generate IG QR code if it doesn't exist
        if not os.path.isfile(qr_file_path):
            url = f'https://www.instagram.com/{username}/'
            qr = qrcode.QRCode(version=1, 
                               error_correction=qrcode.constants.ERROR_CORRECT_L,
                               box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            img.save(qr_file_path)
            print(f"Created QR code for {username}")
        else:
            print(f"QR code already exists for {username}")
            
    except Exception as e:
        print(f"Error creating QR code for {username}: {e}")

    return qr_file_path, '@' + username


def create_qr_code_url(url):
    # create unique filename for the URL QR code
    url_hash = hashlib.md5(url.encode()).hexdigest()
    qr_file_path = f'{QR_DIR}/{url_hash}.png'

    # generate QR code if it doesn't exist
    if not os.path.isfile(qr_file_path):
        try:
            qr = qrcode.QRCode(version=1, 
                               error_correction=qrcode.constants.ERROR_CORRECT_L, 
                               box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            img.save(qr_file_path)
            print(f"Created QR code for URL: {url}")
        except Exception as e:
            print(f"Error creating QR code for URL {url}: {e}")

    return qr_file_path, url


def process_new_message(update):
    # get the UTC time of the message
    message_utc = update.message.forward_date if update.message.forward_date else update.message.date

    # convert to local time zone and format
    local_timezone = pytz.timezone('Australia/Perth')
    message_local_time = message_utc.astimezone(local_timezone)
    message_date_str = message_local_time.strftime('%d %B, %Y %I:%M %p')
    message_file_name_date = message_local_time.strftime('%Y-%m-%d_%I-%M%p')
    
    # get name of the original post creator
    if update.message.forward_from:
        original_author = update.message.forward_from.first_name
    elif update.message.forward_from_chat:
        original_author = update.message.forward_from_chat.title
    else:
        original_author = ""
        
    # construct MD content
    markdown_content = f'## {message_date_str}\n### Message from {original_author}\n\n'
    if update.message.text:
        markdown_content += markdown.markdown(update.message.text)

    # create MD file
    file_name = f'{MARKDOWN_DIR}/{message_file_name_date}.md'
    with open(file_name, 'w') as file:
        file.write(markdown_content)

    # check for tagged usernames and collect QR codes
    qr_codes_for_message = []
    unique_usernames = set(re.findall(r'@([a-zA-Z0-9_.]{1,30})', update.message.text))
    for username in unique_usernames:
        qr_code_data = create_qr_code_ig(username)
        qr_codes_for_message.append(qr_code_data)
            
    # extract URLs and generate QR codes
    url_pattern = r'(https?://\S+|www\.\S+)'
    urls = re.findall(url_pattern, update.message.text)

    # handle URLs
    for url in urls:
        if url.startswith('www.'):
            url = 'http://' + url
        qr_code_data = create_qr_code_url(url)
        if qr_code_data:
            qr_codes_for_message.append(qr_code_data)
    
    return file_name, qr_codes_for_message

def embed_qr_codes_in_markdown(md_file_path, qr_code_data, width=150, height=150):
    with open(md_file_path, 'a') as md_file:
        for qr_path, label in qr_code_data:
            qr_absolute_path = os.path.abspath(qr_path)
            md_file.write(f'<div class="QR"><img src="file://{qr_absolute_path}" width="{width}" height="{height}" alt="QR Code"><span>{label}</span></div>\n')

# convert to HTML
def convert_md_to_html(md_file_path, html_file_path):
    try:
        with open(md_file_path, 'r') as md_file:
            md_content = md_file.read()
        html_content = markdown.markdown(md_content)
        with open(html_file_path, 'w') as html_file:
            # link to external CSS file
            css_path = os.path.abspath('post.css')
            html_file.write(f'<html><head><link rel="stylesheet" type="text/css" href="file://{css_path}"></head><body>\n')            
            # write HTML content
            html_file.write(html_content)
            html_file.write('\n</body></html>')
    except Exception as e:
        print(f"Error converting Markdown to HTML: {e}")


# open HTML file for printing
def open_html(html_file_path):
    webbrowser.open_new_tab(html_file_path)

def process_message(update):
    md_file_path, qr_codes = process_new_message(update)
    # embed QR codes if any
    if qr_codes:
        embed_qr_codes_in_markdown(md_file_path, qr_codes)

    # convert to HTML and open
    html_file_name = os.path.basename(md_file_path).replace('.md', '.html')
    html_file_path = os.path.join(HTML_DIR, html_file_name)
    convert_md_to_html(md_file_path, html_file_path)
    open_html('file://' + os.path.abspath(html_file_path))
        
# handle new messages
def handle_message(update, context):
    print("Handling new message")
    if update.message:
        threading.Thread(target=process_message, args=(update,)).start()

# start listening
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()