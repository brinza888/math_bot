from abc import ABC, abstractmethod

from telebot import TeleBot


class MBModule (ABC):
    def __init__(self, bot: TeleBot, config):
        self.bot: TeleBot = bot
        self.config = config

    @abstractmethod
    def setup(self):
        pass
