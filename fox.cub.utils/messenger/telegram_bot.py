import telegram
from .base import BaseMessenger
from .formatter import BaseFormatter

class TelegramBot(BaseMessenger):

    def __init__(self, api_key: str, chat_id: str,
                 formatter: BaseFormatter):
        self.bot = telegram.Bot(token=api_key)
        self.chat_id = chat_id
        self.formatter = formatter


    def send_message(self, fixture, linedelta):
        self.bot.send_message(text=self.formatter.to_text(fixture, linedelta),
                              chat_id=self.chat_id,
                              parse_mode='Markdown')
