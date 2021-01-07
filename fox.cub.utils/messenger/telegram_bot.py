import telegram
from .base import BaseMessenger


class TelegramBot(BaseMessenger):

    def __init__(self, api_key: str, chat_id: str):
        self.bot = telegram.Bot(token=api_key)
        self.chat_id = chat_id


    def send_message(self, message):
        self.bot.send_message(text=message,
                              chat_id=self.chat_id,
                              parse_mode='Markdown')
