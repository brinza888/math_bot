from math_bot import bot


if __name__ == "__main__":
    print("Copyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    bot.infinity_polling()  # should be infinity to avoid exceptions (#47)
