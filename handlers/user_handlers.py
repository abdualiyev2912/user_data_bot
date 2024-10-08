from aiogram import types, Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from keyboards import inline_keyboards, keyboards
from aiogram.filters import Command
from states.register_state import RegisterStates
from crud import user_crud

async def start_handler(message: types.Message, bot: Bot, state: FSMContext):
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )
    except:
        pass
    finally:
        await state.clear()
        await message.answer("Salom! Botimizga xush kelibsiz!", reply_markup=inline_keyboards.main_menu())

async def register_user(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):  
    await state.set_state(RegisterStates.type)
    await callback_query.message.edit_text("Shaxs turini tanlang:", reply_markup=inline_keyboards.person_type())

async def handle_person_type(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):  
    await state.update_data(type=callback_query.data)
    await state.set_state(RegisterStates.fish)
    await callback_query.message.edit_text("To'liq ismingizni kiriting:")

async def handle_fish(message: types.Message, bot: Bot, state: FSMContext):
    fish_str = message.text
    if len(fish_str.split()) >= 2 and fish_str.replace(" ", "").isalpha():
        await state.update_data(fish=fish_str)
        await state.set_state(RegisterStates.phone)
        await message.answer("To'liq ismingiz qabul qilindi. Endi telefon raqamingizni kiriting:", reply_markup=keyboards.contact())
    else:
        await message.answer("Iltimos, ismingizni to'liq va to'g'ri formatda kiriting:", reply_markup=types.ReplyKeyboardRemove())

async def handle_phone(message: types.Message, bot: Bot, state: FSMContext):
    phone_str = message.text
    if message.contact.phone_number:
        phone_str = message.contact.phone_number
    if (phone_str.isdigit() or phone_str[0]=='+' and phone_str[1:].isdigit()) and len(phone_str) in [10, 13]:  
        user_data = await state.get_data()
        user_data['phone'] = phone_str
        await state.clear()
        await user_crud.create_user({
            "id": message.from_user.id,
            "fish": user_data['fish'],
            "phone": phone_str
        })
        await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz!", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Iltimos, telefon raqamingizni to'g'ri formatda kiriting:", reply_markup=keyboards.contact())

def register_handlers(dp: Dispatcher):    
    dp.message.register(start_handler, Command(commands=['start', 'help']))
    dp.callback_query.register(register_user, lambda c: c.data=='register')
    dp.callback_query.register(handle_person_type, RegisterStates.type)
    dp.message.register(handle_fish, RegisterStates.fish)
    dp.message.register(handle_phone, RegisterStates.phone)