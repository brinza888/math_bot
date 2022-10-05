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

from io import StringIO

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from git import Repo

from config import *
from logic import build_table, OPS
from matrix import Matrix, SizesMatchError, SquareMatrixRequired, NonInvertibleMatrix
from rings import *
from safe_eval import safe_eval, LimitError
from statistics import log_function_call
from models import User, get_db, close_db, ReportRecord

bot = telebot.TeleBot(Config.BOT_TOKEN)

# generate supported logic operators description
logic_ops_description = "\n".join([f"{op} {op_data[3]}" for op, op_data in OPS.items()])

menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)  # this markup is bot menu
menu.add(KeyboardButton("/help"))

menu.add(KeyboardButton("/det"))
menu.add(KeyboardButton("/ref"))
menu.add(KeyboardButton("/m_inverse"))

menu.add(KeyboardButton("/factorize"))
menu.add(KeyboardButton("/euclid"))
menu.add(KeyboardButton("/idempotents"))
menu.add(KeyboardButton("/nilpotents"))
menu.add(KeyboardButton("/inverse"))
menu.add(KeyboardButton("/logic"))

menu.add(KeyboardButton("/calc"))
menu.add(KeyboardButton("/about"))

hide_menu = ReplyKeyboardRemove()  # sending this as reply_markup will close menu


def get_report_menu(user_id):
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text="Сообщить об ошибке!", callback_data="report"))
    if user_id in Config.ADMINS:
        mk.add(InlineKeyboardButton(text="Посмотреть ошибки", callback_data="view_reports"))
    return mk


def get_type_report_menu(user_id):
    mk = InlineKeyboardMarkup(row_width=1)
    new_reports_button = InlineKeyboardButton(text="Новые ошибки", callback_data="report_status_NEW")
    accepted_reports_button = InlineKeyboardButton(text="Принятые ошибки", callback_data="report_status_ACCEPTED")
    rejected_reports_button = InlineKeyboardButton(text="Отклоненные ошибки", callback_data="report_status_REJECTED")
    closed_reports_button = InlineKeyboardButton(text="Закрытые ошибки", callback_data="report_status_CLOSED")
    back_button = InlineKeyboardButton(text="Назад", callback_data="back_button")
    if user_id in Config.ADMINS:
        mk.add(new_reports_button, accepted_reports_button, rejected_reports_button, closed_reports_button, back_button)
    return mk


def get_admin_menu(user_id):
    mk = InlineKeyboardMarkup(row_width=1)
    accept_report_button = InlineKeyboardButton(text="Принять ошибку", callback_data="accept_report")
    reject_report_button = InlineKeyboardButton(text="Отклонить ошибку", callback_data="reject_report")
    close_report_button = InlineKeyboardButton(text="Закрыть ошибку", callback_data="close_report")
    if user_id in Config.ADMINS:
        mk.add(accept_report_button, reject_report_button, close_report_button)
    return mk


@bot.message_handler(commands=["start"])
def start_message(message):
    send_mess = (
        f'<b>Привет{ ", " + message.from_user.first_name if message.from_user.first_name is not None else ""}!</b>\n'
        f'Используй клавиатуру или команды для вызова нужной фишки\n'
        f'/help - вызов помощи\n'
        f'/about - информация о боте'
        )
    bot.send_message(message.chat.id, send_mess, parse_mode="html", reply_markup=menu)
    # User first-time creation
    db = get_db()
    User.get_or_create(db, message.from_user.id, message.from_user.last_name,
                       message.from_user.first_name, message.from_user.username)
    close_db()


@bot.message_handler(commands=["help"])
def send_help(message):
    inline_menu = get_report_menu(message.from_user.id)
    bot.send_message(message.chat.id,
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
                      ),
                     parse_mode="html", reply_markup=inline_menu)


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
        answer = f'Обратная матрица:\n<code>{str(result)}</code>'
        bot.send_message(message.chat.id, answer, parse_mode='html', reply_markup=menu)
        return answer


action_mapper = {
    'det': calc_det,
    'ref': calc_ref,
    'm_inverse': calc_inv
}


def matrix_input(message, action):
    try:
        lst = [[float(x) for x in row.split()] for row in message.text.split('\n')]
        matrix = Matrix.from_list(lst)
    except SizesMatchError:
        bot.reply_to(message,
                     'Несовпадение размеров строк или столбцов. Матрица должна быть <b>прямоугольной</b>.',
                     reply_markup=menu,
                     parse_mode='html')
    except ValueError:
        bot.reply_to(message,
                     'Необходимо вводить <b>числовую</b> квадратную матрицу',
                     reply_markup=menu,
                     parse_mode='html')
    else:
        if matrix.n > Config.MAX_MATRIX:
            bot.reply_to(message, f'Ввод матрицы имеет ограничение в {Config.MAX_MATRIX}x{Config.MAX_MATRIX}!',
                         reply_markup=menu)
        else:
            next_handler = action_mapper[action]
            next_handler(message, action=action, matrix=matrix)


@bot.message_handler(commands=['logic'])
def logic_input(message):
    m = bot.send_message(message.chat.id, f'<u>Допустимые операторы:</u>\n{logic_ops_description}\n\n'
                                          'Введите логическое выражение:',
                         reply_markup=hide_menu,
                         parse_mode="html")
    bot.register_next_step_handler(m, logic_output)


@log_function_call('logic')
def logic_output(message):
    try:
        table, variables = build_table(message.text, Config.MAX_VARS)
        out = StringIO()  # abstract file (file-object)
        print(*variables, 'F', file=out, sep=' ' * 2)
        for row in table:
            print(*row, file=out, sep=' ' * 2)
        answer = f'<code>{out.getvalue()}</code>'
        bot.send_message(message.chat.id, answer, parse_mode='html', reply_markup=menu)
        return answer
    except (AttributeError, SyntaxError):
        bot.send_message(message.chat.id, "Ошибка ввода данных", reply_markup=menu)
    except ValueError:
        bot.send_message(message.chat.id, f"Ограничение по кол-ву переменных: {Config.MAX_VARS}")


@bot.message_handler(commands=['idempotents', 'nilpotents'])
def ring_input(message):
    m = bot.send_message(message.chat.id, 'Введите модуль кольца:')
    bot.register_next_step_handler(m, ring_output, command=message.text[1:])


@log_function_call('ring')
def ring_output(message, command):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    if n >= Config.MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f'Ограничение: 2 <= n < {Config.MAX_MODULO:E}', reply_markup=menu)
        return
    if command == 'idempotents':
        result = [f'{row} -> {el}' for row, el in find_idempotents(n)]
        title = 'Идемпотенты'
    elif command == 'nilpotents':
        result = find_nilpotents(n)
        title = 'Нильпотенты'
    else:
        return
    if len(result) > Config.MAX_ELEMENTS:
        s = 'Элементов слишком много чтобы их вывести...'
    else:
        s = '\n'.join([str(x) for x in result])
    answer = (f'<b> {title} в Z/{n}</b>\n'
              f'Количество: {len(result)}\n\n'
              f'{s}\n')
    bot.send_message(
        message.chat.id,
        answer,
        reply_markup=menu,
        parse_mode='html'
    )
    return answer


@bot.message_handler(commands=['inverse'])
def inverse_input_ring(message):
    m = bot.send_message(message.chat.id, 'Введите модуль кольца:')
    bot.register_next_step_handler(m, inverse_input_element)


def inverse_input_element(message):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    if n >= Config.MAX_MODULO or n < 2:
        bot.send_message(message.chat.id, f'Ограничение: 2 <= n < {Config.MAX_MODULO:E}', reply_markup=menu)
        return
    m = bot.send_message(message.chat.id, 'Введите элемент, для которого требуется найти обратный:')
    bot.register_next_step_handler(m, inverse_output, modulo=n)


@log_function_call('inverse')
def inverse_output(message, modulo):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    n = n % modulo
    try:
        result = find_inverse(n, modulo)
    except ArithmeticError:
        answer = (f'У {n} <b>нет</b> обратного в кольце Z/{modulo}\n'
                  f'Так как НОД({n}, {modulo}) > 1')
        bot.send_message(message.chat.id, answer, parse_mode='html')
        return answer
    else:
        answer = str(result)
        bot.send_message(message.chat.id, answer)
        return answer


@bot.message_handler(commands=['factorize'])
def factorize_input(message):
    m = bot.send_message(message.chat.id, 'Введите число:')
    bot.register_next_step_handler(m, factorize_output)


@log_function_call('factorize')
def factorize_output(message):
    try:
        n = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    if n < 2 or n > Config.FACTORIZE_MAX:
        bot.send_message(
            message.chat.id,
            f'Разложение доступно для положительных целых чисел n: 2 <= n <= {Config.FACTORIZE_MAX:E}'
        )
    else:
        fn = factorize(n)
        answer = f'{n} = ' + factorize_str(fn)
        bot.send_message(message.chat.id, answer)
        return answer


@bot.message_handler(commands=['euclid'])
def euclid_input(message):
    m = bot.send_message(message.chat.id, 'Введите два числа через пробел:')
    bot.register_next_step_handler(m, euclid_output)


@log_function_call('euclid')
def euclid_output(message):
    try:
        a, b = map(int, message.text.strip().split(" "))
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка ввода данных', reply_markup=menu)
        return
    d, x, y = ext_gcd(a, b)
    answer = (f'НОД({a}, {b}) = {d}\n\n'
              f"<u>Решение уравнения:</u>\n{a}*x + {b if b >= 0 else f'({b})'}*y <b>= {d}</b>\n"
              f'x = {x}\ny = {y}\n\n'
              f'<u>Внимание</u>\n'
              f'<b>Обращайте внимание на вид уравнения!</b>\n'
              f'Решается уравнение вида ax + by = НОД(a, b)!')
    bot.send_message(message.chat.id, answer, parse_mode='html')
    return answer


@bot.message_handler(commands=['calc'])
def calc_input(message):
    m = bot.send_message(message.chat.id, 'Операция возведения в степень обозначается <b>^</b>\n\n'
                                          'Введите выражение:',
                         parse_mode="html")
    bot.register_next_step_handler(m, calc_output)


@log_function_call('calc')
def calc_output(message):
    try:
        answer = str(safe_eval(message.text))
    except (SyntaxError, TypeError):
        bot.send_message(message.chat.id, 'Синтаксическая ошибка в выражении', reply_markup=menu)
    except LimitError:
        bot.send_message(message.chat.id, 'Достигнут лимит возможной сложности вычислений', reply_markup=menu)
    except ZeroDivisionError:
        bot.send_message(message.chat.id, 'Деление на 0 не определено')
    except ArithmeticError:
        bot.send_message(message.chat.id, 'Арифметическая ошибка')
    else:
        bot.send_message(message.chat.id, answer, parse_mode='html')
        return answer


@bot.message_handler(commands=["broadcast", "bc"])
def broadcast_input(message):
    if message.from_user.id not in Config.ADMINS:
        return
    m = bot.send_message(message.chat.id, "Сообщение для рассылки:")
    bot.register_next_step_handler(m, broadcast)


def broadcast(message):
    db = get_db()
    for user in db.query(User).all():
        bot.send_message(user.id, message.text)
    close_db()


@bot.message_handler(commands=['about'])
def send_about(message):
    repo = Repo('./')
    version = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)
    warning = ""
    if not version:
        version = repo.head.commit.hexsha
        warning = " (<u>нестабильная</u>)"
    bot.send_message(message.chat.id,
                     f"Версия{warning}: <b>{version}</b>\n\n"
                     "Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin\n"
                     f"GitHub: {Config.GITHUB_LINK}\n"
                     "<b>Под лицензией GNU-GPL 2.0-or-latter</b>",
                     parse_mode="html")


@bot.callback_query_handler(func=lambda call: call.data == "report")
def callback_inline(call):
    m = bot.send_message(call.message.chat.id, "Some text for user how to fill report")
    bot.register_next_step_handler(m, report_handling)


def report_handling(message):
    db = get_db()
    user = User.get_or_create(db, message.from_user.id, message.from_user.last_name,
                                          message.from_user.first_name, message.from_user.username)
    rec = ReportRecord.new(user, message.text)
    db.add(rec)
    db.commit()
    close_db()
    bot.send_message(message.chat.id, "Спасибо, что сообщаете нам о проблемах!")


@bot.callback_query_handler(func=lambda call: call.data == "view_reports")
def choose_report_types(call):
    mk = get_type_report_menu(call.from_user.id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=mk)


@bot.callback_query_handler(func=lambda call: call.data == "report_status_NEW" or call.data == "report_status_REJECTED" or
                                              call.data == "report_status_ACCEPTED" or call.data == "report_status_CLOSED")
def list_reports(call):
    db = get_db()
    reports = ReportRecord.get_reports(db, call.data)
    close_db()
    mk = get_admin_menu(call.from_user.id)
    for report in reports:
        bot.send_message(chat_id=call.message.chat.id, text=f'Report id: {report.id}\nUser id: {report.user_id}\n'
                                                            f'Timestamp: {report.timestamp}\n\n'
                                                            f'Problem statement:\n{report.text}\n\n'
                                                            f'Status: <b>{report.status}</b>\nLink: {report.link}',
                         parse_mode="html", reply_markup=mk)


@bot.callback_query_handler(func=lambda call: call.data == "accept_report" or call.data == "reject_report" or
                            call.data == "close_report")
def change_report_status(call):
    db = get_db()
    id = call.message.text.split()[2]
    if call.data == "accept_report":
        m = bot.send_message(call.message.chat.id, "Предоставьте ссылку на Github Issue")
        bot.register_next_step_handler(m, link_handling, id)
    if call.data == "close_report":
        if ReportRecord.get_report_by_id(db, id).status == "ACCEPTED":
            ReportRecord.change_status(db, id, call.data)
            bot.send_message(call.message.chat.id, "Ошибка закрыта")
        else:
            bot.send_message(call.message.chat.id, "Ошибка еще не подтверждена!")
    if call.data == "reject_report":
        ReportRecord.change_status(db, id, call.data)
        bot.send_message(call.message.chat.id, "Ошибка отклонена")
    close_db()


def link_handling(message, id):
     mk = InlineKeyboardMarkup(row_width=1)
     mk.add(InlineKeyboardButton(text="Подтвердить", callback_data=f"accept_link {id}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"reject_link {id}"))
     bot.send_message(message.chat.id, text=f"<b>Верна ли указана ссылка?</b>\n<b>Link:</b> {message.text}",
                      parse_mode="html", reply_markup=mk)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == "accept_link" or
                                              call.data.split()[0] == "reject_link")
def accept_link(call):
    db = get_db()
    id = int(call.data.split()[1])
    if call.data.split()[0] == "accept_link":
        ReportRecord.change_status(db, id, "accept_report", call.message.text.split('\n')[1].split()[1])
        bot.send_message(call.message.chat.id, "Ошибка подтверждена")
    else:
        bot.send_message(call.message.chat.id, text="Укажите ссылку еще раз")
        bot.register_next_step_handler(call.message, link_handling, id)
    close_db()


@bot.callback_query_handler(func=lambda call: call.data == "back_button")
def back_func(call):
    mk = get_report_menu(call.from_user.id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=mk)


if __name__ == "__main__":
    print("Copyright (C) 2021-2022 Ilya Bezrukov, Stepan Chizhov, Artem Grishin")
    print("Licensed under GNU GPL-2.0-or-later")
    bot.polling(none_stop=True)
