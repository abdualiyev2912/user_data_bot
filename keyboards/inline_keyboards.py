from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Ro'yxatdan o'tish", callback_data="register")]])
    return inline_keyboard

def person_type():
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Yuridik", callback_data="yuridik"),
            InlineKeyboardButton(text="Jismoniy", callback_data="jismoniy")
        ]])
    return inline_keyboard