# -*- coding: utf-8 -*-
import telebot
from matrix import minor
from matrix import det
from telebot import types
import requests
from io import BytesIO

from logic import shunting_yard, calculate

operators = {
    "~": ("Логическое отрицание",),
    "&": ("Конъюнкция",),
    "|": ("Дизъюнкция",),
    ">": ("Импликация",),
    "^": ("Исключающее или",),
    "=": ("Эквиваленция",),
}

HELP_STR = "\n".join([f"<b>{op}</b> {op_info[0]}" for op, op_info in operators.items()])


with open("token.txt") as tk:
    bot = telebot.TeleBot(tk.read())


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(types.KeyboardButton('Помощь'))
    markup.add(types.KeyboardButton('Что ты умеешь?'))
    markup.add(types.KeyboardButton('Список операторов'))
    send_mess = f"<b>Привет {message.from_user.first_name} {message.from_user.last_name}!</b>\nНажми на кнопку, чтобы узнать, что я умею"
    bot.send_message(message.chat.id, send_mess, parse_mode='html', reply_markup=markup)


@bot.message_handler(regexp="список операторов")
def send_ops(message):
    bot.send_message(message.chat.id, HELP_STR, parse_mode='html')

@bot.message_handler(regexp="помощь")
def send_ops(message):
    bot.send_message(message.chat.id, "Напишите 'матрица' или 'определитель' для нахождения определителя матрицы. Введите логическое выражение для построения таблицы истинности.", parse_mode='html')

@bot.message_handler(regexp="Что ты умеешь?")
def send_help(message):
    bot.send_message(message.chat.id, 'Я бот, который умеет строить таблицы истинности и считать определители квадратных матриц.', parse_mode='html')

@bot.message_handler(regexp="матрица|определитель")
def matsize(message): #Ввод размеров матрицы и матрицы
    try:   #для избежания ошибок - пользователь может ввести строку вместо числа
        sendsize = bot.send_message(message.chat.id, "Введите размер матрицы:")
        bot.register_next_step_handler(sendsize, matrixinput)  #Переходит к шагу matrixinput с переменной sendmsg
    except Exception:
        pass
def matrixinput(message):
    try:
        sendmatr = bot.send_message(message.chat.id, "Введите матрицу:")
        bot.register_next_step_handler(sendmatr, output)
    except Exception:
        pass
def output(message):
    try:
        text=str(message.text)
        matric = [[int(x) for x in row.split()] for row in text.split('\n')]
        bot.send_message(message.chat.id, str(det(matric)))
    except Exception:
        pass

@bot.message_handler(regexp="&|\||>|~|\^|=")
def handle_ops(message):
    out, variables = shunting_yard(message.text)
    n = len(variables)
    variables_print = ''
    for v in variables:
        variables_print += str(v).ljust(6)
    variables_print += 'F'.ljust(6) + '\n'

    for i in range(2 ** n):
        values = [int(x) for x in bin(i)[2:].rjust(n, "0")]
        d = {variables[k]: values[k] for k in range(n)}
        for v in values:
            variables_print += str(v).ljust(6)
        variables_print += str(int(calculate(out, d))).ljust(6) + '\n'

    bot.send_message(message.chat.id, variables_print)

@bot.message_handler(regexp="ахуеть")    #отдельный хендлер картинки
def get_text_messages(message):
    r = requests.get('https://www.meme-arsenal.com/memes/ddcf6ef709b8db99da11efd281abd990.jpg')
    MEM_IMAGE = BytesIO(r.content)  # BytesIO creates file-object from bytes string
    bot.send_photo(message.chat.id, MEM_IMAGE)

bot.polling(none_stop=True)
