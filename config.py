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
