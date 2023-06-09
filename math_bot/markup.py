from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,\
    InlineKeyboardButton, InlineKeyboardMarkup

from math_bot.config import Config


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


def get_cancel_menu():
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text="Назад", callback_data="cancel"))
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


def get_admin_menu(call):
    mk = InlineKeyboardMarkup(row_width=1)
    if call.data not in ["report_status_CLOSED", "report_status_REJECTED"] and call.from_user.id in Config.ADMINS:
        if call.data not in ["report_status_ACCEPTED"]:
            accept_report_button = InlineKeyboardButton(text="Принять ошибку", callback_data="accept_report")
            mk.add(accept_report_button)
        reject_report_button = InlineKeyboardButton(text="Отклонить ошибку", callback_data="reject_report")
        close_report_button = InlineKeyboardButton(text="Закрыть ошибку", callback_data="close_report")
        mk.add(reject_report_button, close_report_button)
        return mk
