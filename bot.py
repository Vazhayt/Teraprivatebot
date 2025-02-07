import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = '8012804738:AAEkIvfM03F3ZPtACdYtao1TunjhCZhpDik'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Send me a TeraBox link to download the file.')

def get_download_link(terabox_url):
    session = requests.Session()
    response = session.get(terabox_url)
    
    if response.status_code != 200:
        raise Exception("Failed to access TeraBox link.")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    download_button = soup.find('a', class_='download-button')  # Adjust this selector
    if download_button and 'href' in download_button.attrs:
        download_link = download_button['href']
        return download_link
    else:
        raise Exception("Download link not found.")

async def download_terabox(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if 'terabox.com' in url:
        await update.message.reply_text('Downloading your file...')
        try:
            download_link = get_download_link(url)
            response = requests.get(download_link, stream=True)
            if response.status_code == 200:
                filename = 'downloaded_file'  # You can customize the filename
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                await update.message.reply_document(document=open(filename, 'rb'))
            else:
                await update.message.reply_text('Failed to download the file. Please check the link.')
        except Exception as e:
            await update.message.reply_text(f'An error occurred: {e}')
    else:
        await update.message.reply_text('Please send a valid TeraBox link.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await download_terabox(update, context)

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()