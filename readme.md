# Telegram QR Code Bot

This Telegram bot was created to streamline the process of printing recent messages from the "Daily Updates 🇵🇸" channel.

It generates QR codes for Instagram usernames and URLs mentioned in messages. It is designed to listen to messages sent to it or forwarded from other chats, process the content, and create corresponding QR codes. The bot also converts the messages into HTML format, embedding the QR codes for easy viewing and printing.

## Prerequisites

Before running the script, make sure you have the following:

- Python 3 installed
- Telegram Bot Token: Obtain a token by creating a new bot on Telegram using the [BotFather](https://telegram.me/BotFather).

## Installation

1. Clone the repository:

```
git clone https://github.com/your_username/daily_updates_telegram.git
cd daily_updates_telegram
```

2. Create and activate a virtual environment (optional but recommended):

```
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Initialise environment variables:

- Create a `.env` file in the project root.
- Add your Telegram bot token:

```
TELEGRAM_TOKEN=<your_telegram_token>
```

5. Running the bot:

```
python bot_script.py
```

## Usage

After starting the bot:

- Send a message directly to the bot or forward a message from another chat.
- The bot will process Instagram usernames and URLs, generating QR codes for each.
- A Markdown file is created for each message, which is then converted to an HTML file.
- The HTML file, with embedded QR codes, will open in your default web browser.

## Customisation

- Directories: The script creates two directories, `telegram_data` and `QR_codes`, to store the generated files.

- QR code size: By default, the QR codes are generated with a width and height of 150 pixels. You can adjust the size by modifying the `width` and `height` parameters in the `embed_qr_codes_in_markdown` function.

- Styling: The HTML output is styled using an external CSS file named `post.css`. You can customise the styling by modifying this CSS file.

## Contributing

Contributions and suggestions to this project are welcome.
