import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///bot.db")
    DEBUG = bool(int(os.getenv("DEBUG", 0)))
    BOT_TOKEN = os.getenv("BOT_TOKEN")

