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

import os
from telebot.apihelper import ApiTelegramException
from git import Repo

from math_bot import bot
from math_bot.statistics import get_db, close_db
from math_bot.models import User, ReportRecord
from math_bot.markup import *


@bot.message_handler(commands=["start"])
def start_message(message):
    send_mess = (
        f"<b>Привет{ ', ' + message.from_user.first_name if message.from_user.first_name is not None else ''}!</b>\n"
        f"Используй клавиатуру или команды для вызова нужной фишки\n"
        f"/help - вызов помощи\n"
        f"/about - информация о боте\n"
        f"Наш канал: {Config.CHANNEL_LINK}\n"
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


@bot.message_handler(commands=["broadcast", "bc"])
def broadcast_input(message):
    if message.from_user.id not in Config.ADMINS:
        return
    m = bot.send_message(message.chat.id, "Сообщение для рассылки:")
    bot.register_next_step_handler(m, broadcast)


def broadcast(message):
    db = get_db()
    blocked_count = 0
    for user in db.query(User).all():
        try:
            bot.send_message(user.id, message.text)
        except ApiTelegramException:
            blocked_count += 1
    bot.send_message(message.chat.id, "Рассылка успешно завершена!\n"
                                      f"Не получили рассылку: {blocked_count}")
    close_db()


@bot.message_handler(commands=["about"])
def send_about(message):
    repo = Repo(os.getcwd())
    version = next((tag for tag in repo.tags if tag.commit == repo.head.commit), None)
    warning = ""
    if not version:
        version = repo.head.commit.hexsha
        warning = " (<u>нестабильная</u>)"
    bot.send_message(message.chat.id,
                     f"Версия{warning}: <b>{version}</b>\n"
                     f"Наш канал: {Config.CHANNEL_LINK}\n"
                     f"\nCopyright (C) 2021-2023 Ilya Bezrukov, Stepan Chizhov, Artem Grishin\n"
                     f"GitHub: {Config.GITHUB_LINK}\n"
                     f"<b>Под лицензией GNU-GPL 2.0-or-latter</b>",
                     parse_mode="html")


@bot.callback_query_handler(func=lambda call: call.data == "report")
def callback_inline(call):
    mk = get_cancel_menu()
    m = bot.send_message(call.message.chat.id, "Опишите что именно пошло не так", reply_markup=mk)
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


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_report(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.clear_step_handler_by_chat_id(call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == "view_reports")
def choose_report_types(call):
    mk = get_type_report_menu(call.from_user.id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=mk)


@bot.callback_query_handler(func=lambda call: call.data in ("report_status_NEW", "report_status_REJECTED",
                                                            "report_status_ACCEPTED", "report_status_CLOSED"))
def list_reports(call):
    db = get_db()
    reports = ReportRecord.get_reports(db, call.data)
    close_db()
    mk = get_admin_menu(call)
    for report in reports:
        bot.send_message(chat_id=call.message.chat.id, text=f"Report id: {report.id}\nUser id: {report.user_id}\n"
                                                            f"Timestamp: {report.timestamp}\n\n"
                                                            f"Problem statement:\n{report.text}\n\n"
                                                            f"Status: <b>{report.status}</b>\nLink: {report.link}",
                         parse_mode="html", reply_markup=mk)


@bot.callback_query_handler(func=lambda call: call.data in ("accept_report", "reject_report", "close_report"))
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
    bot.send_message(message.chat.id, text=f"<b>Верно ли указана ссылка?</b>\n<b>Link:</b> {message.text}",
                     parse_mode="html", reply_markup=mk)


@bot.callback_query_handler(func=lambda call: call.data.split()[0] in ("accept_link", "reject_link"))
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
