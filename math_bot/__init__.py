# -*- coding: utf-8 -*-

# Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
#
# This file is part of math_bot.
#
# math_bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
#
# math_bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
