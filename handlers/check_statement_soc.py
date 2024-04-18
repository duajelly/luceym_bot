import datetime as dt
import time, os
os.environ['TZ'] = 'Asia/Yekaterinburg'

import sql_conf
from handlers.main import sth_wrong as wrong
from analytics import send_analytics

from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router

router = Router()

class UserApplicChekForm(StatesGroup):
    code = State()

@router.message(Command(commands=['checkcode']))
async def start(message: Message, state: FSMContext) -> None:
    await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='check_code')
    await message.answer("Введите код заявления", reply_markup=ReplyKeyboardMarkup(
                                        keyboard=[[KeyboardButton(text="Отменить")]], resize_keyboard=True  
                                    ))
    await state.set_state(UserApplicChekForm.code)

@router.message(Command(commands=["cancel"]))
@router.message(F.text.casefold() == "cancel", F.text.casefold() == "отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup = ReplyKeyboardRemove(),
    )  

@router.message(UserApplicChekForm.code)
async def photo_err(message: Message, state: FSMContext) -> None:
    try:
        cnx = sql_conf.mysql_create()
        event_query = (f"SELECT * FROM statements_bucket WHERE code = '{message.text}'")
        with cnx.cursor() as cursor:
            cursor.execute(event_query)
            result = cursor.fetchall()

            count_row = 0
            global user_id
            for row in result:
                photo_id = row[5]
                confirm = row[7]
                number = row[1]
                date = time.strftime('%d.%m.%y', time.gmtime(row[4]))
                count_row += 1
            
            message_next = (
                '\nФамилия: Ожидание'
                '\nИмя: Ожидание'
                '\nОтчество: Ожидание'
                '\nКласс: Ожидание'
                '\nВыезд: Ожидание'
                '\nЗаезд: Ожидание'
            )

            if count_row:
                if confirm == 4 and not number:
                    await message.answer("Заявление согласовано\n(Здорик А.С.)\nВ процессе регистрации", reply_markup=ReplyKeyboardRemove())
                elif number:
                    await message.answer(f"Заявление согласовано\n(Здорик А.С.)\nРегистрация №{number}\nот {date}", reply_markup=ReplyKeyboardRemove())
                elif confirm == 1:
                    await message.answer("Согласовано (Здорик АС).\nБез требования регистрации.", reply_markup=ReplyKeyboardRemove())
                elif confirm == 0 and photo_id:
                    await message.answer("В процессе согласования", reply_markup=ReplyKeyboardRemove())
                else:
                    await message.answer("Такого заявления не существует, либо оно не согласовано", reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("Такого заявления не существует, либо оно не согласовано", reply_markup=ReplyKeyboardRemove())

            cnx.close()
    except Exception as e:
        await wrong(message, e)