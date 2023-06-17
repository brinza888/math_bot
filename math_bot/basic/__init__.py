import os

from git import Repo
from telebot.apihelper import ApiTelegramException

from math_bot.module import MBModule
from math_bot.models import get_db, close_db, User
from math_bot import markup


class BasicModule(MBModule):
    def setup(self):
        self.bot.register_message_handler(self.start_message, commands=["start"])
        self.bot.register_message_handler(self.send_help, commands=["help"])
        self.bot.register_message_handler(self.send_about, commands=["about"])
        self.bot.register_message_handler(self.broadcast_input, commands=["broadcast", "bc"])

    def start_message(self, message):
        send_mess = (
            f"<b>Привет{', ' + message.from_user.first_name if message.from_user.first_name is not None else ''}!</b>\n"
            f"Используй клавиатуру или команды для вызова нужной фишки\n"
            f"/help - вызов помощи\n"
            f"/about - информация о боте\n"
            f"Наш канал: {self.config.CHANNEL_LINK}\n"
        )
        self.bot.send_message(message.chat.id, send_mess, reply_markup=markup.menu)
        # User first-time creation
        db = get_db()
        User.get_or_create(db, message.from_user.id, message.from_user.last_name,
                           message.from_user.first_name, message.from_user.username)
        close_db()

    def send_help(self, message):
        # TODO: add reply_markup for reports
        self.bot.send_message(message.chat.id,
                              ("<b>Работа с матрицами</b>\n"
                               "/det - определитель матрицы.\n"
                               "/ref - ступенчатый вид матрицы (верхне-треугольный).\n"
                               "/m_inverse - обратная матрица.\n"
                               "\n<b>Теория чисел и дискретная математика</b>\n"
                               "/factorize - разложение натурального числа в простые.\n"
                               "/euclid - НОД двух чисел и решение Диофантового уравнения.\n"
                               "/idempotents - идемпотентные элементы в Z/n.\n"
                               "/nilpotents - нильпотентные элементы в Z/n.\n"
                               "/inverse - обратный элемент в Z/n.\n"
                               "/logic - таблица истинности выражения.\n"
                               "\n<b>Калькуляторы</b>\n"
                               "/calc - калькулятор математических выражений.\n"
                               "\n<b>Об этом боте</b> /about\n"
                               ))

    def broadcast_input(self, message):
        if message.from_user.id not in self.config.ADMINS:
            return
        m = self.bot.send_message(message.chat.id, "Сообщение для рассылки:")
        self.bot.register_next_step_handler(m, self.broadcast)

    def broadcast(self, message):
        db = get_db()
        blocked_count = 0
        for user in db.query(User).all():
            try:
                self.bot.send_message(user.id, message.text)
            except ApiTelegramException:
                blocked_count += 1
        self.bot.send_message(message.chat.id, "Рассылка успешно завершена!\n"
                                               f"Не получили рассылку: {blocked_count}")
        close_db()

    def send_about(self, message):
        repo = Repo(os.getcwd())
        version = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)
        warning = ""
        if not version:
            version = repo.head.commit.hexsha
            warning = " (<u>нестабильная</u>)"
        self.bot.send_message(message.chat.id,
                              f"Версия{warning}: <b>{version}</b>\n"
                              f"Наш канал: {self.config.CHANNEL_LINK}\n"
                              f"\nCopyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin\n"
                              f"GitHub: {self.config.GITHUB_LINK}\n"
                              f"<b>Под лицензией GNU-GPL 2.0-or-latter</b>")
