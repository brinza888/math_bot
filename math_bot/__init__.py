import telebot

from math_bot.config import Config

from .basic import BasicModule
from .matrix import MatrixModule
from .numbers import NumbersModule
from .calculators import CalculatorModule, LogicModule


def create_bot(config: Config = Config()):
    bot = telebot.TeleBot(Config.BOT_TOKEN)
    bot.parse_mode = "html"

    BasicModule(bot, config).setup()
    NumbersModule(bot, config).setup()
    MatrixModule(bot, config).setup()
    CalculatorModule(bot, config).setup()
    LogicModule(bot, config).setup()

    return bot
