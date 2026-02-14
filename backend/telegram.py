import requests
import json
import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'bot8463614992:AAGz3ATzcNgPXEmlaKHsdb0vmlBSrTV37is')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '5666336063')
TELEGRAM_API_URL = f'https://api.telegram.org/{TELEGRAM_TOKEN}'

def send_message(text, parse_mode='Markdown'):
    """Send a message to the configured Telegram chat."""
    url = f'{TELEGRAM_API_URL}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': parse_mode
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f'Telegram send error: {e}')
        return None

def notify_success(message):
    """Send a success notification."""
    send_message(f'✅ {message}')

def notify_error(message):
    """Send an error notification."""
    send_message(f'⚠️ {message}')

def notify_decision(message, question):
    """Send a decision request."""
    send_message(f'❓ {message}\n\n{question}\n\nReply with YES/NO')

def notify_status(message):
    """Send a status update."""
    send_message(f'🔄 {message}')

def notify_info(message):
    """Send an info notification."""
    send_message(f'ℹ️ {message}')

if __name__ == '__main__':
    result = send_message('🤖 Test message from MuttLogbook - messaging is working!')
    print('Message sent:', result)
