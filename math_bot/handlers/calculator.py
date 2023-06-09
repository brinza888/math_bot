from math_bot import bot, log_function_call
from math_bot.markup import *
from math_bot.core.safe_eval import safe_eval
from math_bot.core import shunting_yard as sy


@bot.message_handler(commands=["calc"])
def calc_input(message):
    m = bot.send_message(message.chat.id, "Введите выражение:", parse_mode="html")
    bot.register_next_step_handler(m, calc_output)


@log_function_call("calc")
def calc_output(message):
    try:
        answer = str(safe_eval(message.text))
    except sy.InvalidSyntax:
        bot.send_message(message.chat.id, "Синтаксическая ошибка в выражении", reply_markup=menu)
    except sy.InvalidName:
        bot.send_message(message.chat.id, "Встречена неизвестная переменная", reply_markup=menu)
    except sy.InvalidArguments:
        bot.send_message(message.chat.id, "Неправильное использование функции")
    except sy.CalculationLimitError:
        bot.send_message(message.chat.id, "Достигнут лимит возможной сложности вычислений", reply_markup=menu)
    except ZeroDivisionError:
        bot.send_message(message.chat.id, "Во время выполнения встречено деление на 0", reply_markup=menu)
    except ArithmeticError:
        bot.send_message(message.chat.id, "Арифметическая ошибка", reply_markup=menu)
    except ValueError:
        bot.send_message(message.chat.id, "Не удалось распознать значение", reply_markup=menu)
    else:
        bot.send_message(message.chat.id, answer, parse_mode="html", reply_markup=menu)
        return answer
