from math_bot.module import MBModule
from math_bot import markup

from .numbers import *


class NumbersModule (MBModule):
    def setup(self):
        self.bot.register_message_handler(self.ring_input, commands=["nilpotents", "idempotents"])
        self.bot.register_message_handler(self.inverse_input_ring, commands=["inverse"])
        self.bot.register_message_handler(self.euclid_input, commands=["euclid"])

    def ring_input(self, message):
        m = self.bot.send_message(message.chat.id, "Введите модуль кольца:")
        self.bot.register_next_step_handler(m, self.ring_output, command=message.text[1:])

    def ring_output(self, message, command):
        try:
            n = int(message.text.strip())
        except ValueError:
            self.bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=markup.menu)
            return
        if n >= self.config.MAX_MODULO or n < 2:
            self.bot.send_message(message.chat.id, f"Ограничение: 2 <= n < {self.config.MAX_MODULO:E}",
                                  reply_markup=markup.menu)
            return
        if command == "idempotents":
            result = [f"{row} -> {el}" for row, el in find_idempotents(n)]
            title = "Идемпотенты"
        elif command == "nilpotents":
            result = find_nilpotents(n)
            title = "Нильпотенты"
        else:
            return
        if len(result) > self.config.MAX_ELEMENTS:
            s = "Элементов слишком много чтобы их вывести..."
        else:
            s = "\n".join([str(x) for x in result])
        answer = (f"<b> {title} в Z/{n}</b>\n"
                  f"Количество: {len(result)}\n\n"
                  f"{s}\n")
        self.bot.send_message(
            message.chat.id,
            answer,
            reply_markup=markup.menu,
            parse_mode="html"
        )
        return answer

    def inverse_input_ring(self, message):
        m = self.bot.send_message(message.chat.id, "Введите модуль кольца:")
        self.bot.register_next_step_handler(m, self.inverse_input_element)

    def inverse_input_element(self, message):
        try:
            n = int(message.text.strip())
        except ValueError:
            self.bot.send_message(message.chat.id, "Ошибка ввода данных",
                                  reply_markup=markup.menu)
            return
        if n >= self.config.MAX_MODULO or n < 2:
            self.bot.send_message(message.chat.id, f"Ограничение: 2 <= n < {self.config.MAX_MODULO:E}",
                                  reply_markup=markup.menu)
            return
        m = self.bot.send_message(message.chat.id, "Введите элемент, для которого требуется найти обратный:")
        self.bot.register_next_step_handler(m, self.inverse_output, modulo=n)

    def inverse_output(self, message, modulo):
        try:
            n = int(message.text.strip())
        except ValueError:
            self.bot.send_message(message.chat.id, "Ошибка ввода данных",
                                  reply_markup=markup.menu)
            return
        n = n % modulo
        try:
            result = find_inverse(n, modulo)
        except ArithmeticError:
            answer = (f"У {n} <b>нет</b> обратного в кольце Z/{modulo}\n"
                      f"Так как НОД({n}, {modulo}) > 1")
            self.bot.send_message(message.chat.id, answer, parse_mode="html")
            return answer
        else:
            answer = str(result)
            self.bot.send_message(message.chat.id, answer)
            return answer

    def factorize_input(self, message):
        m = self.bot.send_message(message.chat.id, "Введите число:")
        self.bot.register_next_step_handler(m, self.factorize_output)

    def factorize_output(self, message):
        try:
            n = int(message.text.strip())
        except ValueError:
            self.bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=markup.menu)
            return
        if n < 2 or n > self.config.FACTORIZE_MAX:
            self.bot.send_message(
                message.chat.id,
                f"Разложение доступно для положительных целых чисел n: 2 <= n <= {self.config.FACTORIZE_MAX:E}"
            )
        else:
            fn = factorize(n)
            answer = f"{n} = " + factorize_str(fn)
            self.bot.send_message(message.chat.id, answer)
            return answer

    def euclid_input(self, message):
        m = self.bot.send_message(message.chat.id, "Введите два числа через пробел:")
        self.bot.register_next_step_handler(m, self.euclid_output)

    def euclid_output(self, message):
        try:
            a, b = map(int, message.text.strip().split(" "))
        except ValueError:
            self.bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=markup.menu)
            return
        d, x, y = ext_gcd(a, b)
        answer = (f"НОД({a}, {b}) = {d}\n\n"
                  f"<u>Решение уравнения:</u>\n{a}*x + {b if b >= 0 else f'({b})'}*y <b>= {d}</b>\n"
                  f"x = {x}\ny = {y}\n\n"
                  f"<u>Внимание</u>\n"
                  f"<b>Обращайте внимание на вид уравнения!</b>\n"
                  f"Решается уравнение вида ax + by = НОД(a, b)!")
        self.bot.send_message(message.chat.id, answer, parse_mode="html")
        return answer
