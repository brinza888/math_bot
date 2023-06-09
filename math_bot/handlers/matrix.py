from math_bot import bot, log_function_call
from math_bot.markup import *
from math_bot.core import Matrix, SquareMatrixRequired, SizesMatchError, NonInvertibleMatrix


@bot.message_handler(commands=["det"])
def det(message):
    m = bot.send_message(message.chat.id, "Введите матрицу: (одним сообщением)", reply_markup=hide_menu)
    bot.register_next_step_handler(m, matrix_input, action="det")


@log_function_call("det")
def calc_det(message, action, matrix):
    try:
        result = matrix.det()
    except SquareMatrixRequired:
        bot.reply_to(message, "Невозможно рассчитать определитель для не квадратной матрицы!", reply_markup=menu)
    else:
        answer = str(result)
        bot.reply_to(message, answer, reply_markup=menu)
        return answer


@bot.message_handler(commands=["ref"])
def ref_input(message):
    m = bot.send_message(message.chat.id, "Введите матрицу: (одним сообщением)", reply_markup=hide_menu)
    bot.register_next_step_handler(m, matrix_input, action="ref")


@log_function_call("ref")
def calc_ref(message, action, matrix):
    result = matrix.ref()
    answer = f"Матрица в ступенчатом виде:\n<code>{str(result)}</code>"
    bot.send_message(message.chat.id, answer, parse_mode="html", reply_markup=menu)
    return answer


@bot.message_handler(commands=["m_inverse"])
def inv_input(message):
    m = bot.send_message(message.chat.id, "Введите матрицу: (одним сообщением)", reply_markup=hide_menu)
    bot.register_next_step_handler(m, matrix_input, action="m_inverse")


@log_function_call("m_inverse")
def calc_inv(message, action, matrix):
    try:
        result = matrix.inverse()
    except NonInvertibleMatrix:
        bot.send_message(message.chat.id, "Обратной матрицы не существует!", reply_markup=menu)
        return
    else:
        answer = f"Обратная матрица:\n<code>{str(result)}</code>"
        bot.send_message(message.chat.id, answer, parse_mode="html", reply_markup=menu)
        return answer


action_mapper = {
    "det": calc_det,
    "ref": calc_ref,
    "m_inverse": calc_inv
}


def matrix_input(message, action):
    try:
        lst = [[float(x) for x in row.split()] for row in message.text.split("\n")]
        matrix = Matrix.from_list(lst)
    except SizesMatchError:
        bot.reply_to(message,
                     "Несовпадение размеров строк или столбцов. Матрица должна быть <b>прямоугольной</b>.",
                     reply_markup=menu,
                     parse_mode="html")
    except ValueError:
        bot.reply_to(message,
                     "Необходимо вводить <b>числовую</b> квадратную матрицу",
                     reply_markup=menu,
                     parse_mode="html")
    else:
        if matrix.n > Config.MAX_MATRIX:
            bot.reply_to(message, f"Ввод матрицы имеет ограничение в {Config.MAX_MATRIX}x{Config.MAX_MATRIX}!",
                         reply_markup=menu)
        else:
            next_handler = action_mapper[action]
            next_handler(message, action=action, matrix=matrix)
