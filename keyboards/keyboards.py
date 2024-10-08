from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def contact():
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Raqamni ulashish", request_contact=True)]
        ]
    )
