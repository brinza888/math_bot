# -*- coding: utf-8 -*-

# Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin
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

import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    # SET UP
    DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///bot.db")
    DEBUG = bool(int(os.getenv("DEBUG", 0)))
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    # CALCULATION LIMITS
    # max matrix size
    MAX_MATRIX = int(os.getenv("MAX_MATRIX", 8))
    # max variables count in logic expression
    MAX_VARS = int(os.getenv("MAX_VARS", 7))
    # max rings modulo
    MAX_MODULO = int(os.getenv("MAX_MODULO", 10**15))
    # max elements to list in message
    MAX_ELEMENTS = int(os.getenv("MAX_VARS", 101))
    # max number that can be factorized
    FACTORIZE_MAX = int(os.getenv("MAX_VARS", 10 ** 12))
