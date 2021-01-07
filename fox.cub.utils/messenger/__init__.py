from .base import BaseMessenger
from .telegram_bot import TelegramBot
from config import Config

def messenger_factory(messenger_type):
    conf = Config()['messengers']

    if messenger_type == 'telegram':
        return TelegramBot(conf['telegram']['apiKey'],
                                conf['telegram']['id'])

    raise TypeError("Invalid messenger type")
