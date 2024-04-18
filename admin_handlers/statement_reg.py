import datetime as dt
import time, os
os.environ['TZ'] = 'Asia/Yekaterinburg'

from config import bot
import sql_conf
from handlers.main import sth_wrong as wrong
from handlers.main import unknown_func
from admin_handlers.access_groups import STATEMENT_REG_ADMIN

from aiogram.types import Message
from aiogram.filters import Command, CommandObject, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram import F, Router, types, html

router = Router()

class AdminStatementRegForm(StatesGroup):
    code = State()
    confirm = State()
    reg_num = State() 

router = Router()

@router.message(Command(commands=['statement_reg']))
async def start(message: Message, state: FSMContext) -> None:
    if message.from_user.id == STATEMENT_REG_ADMIN:       
        await message.answer("Введите код заявления", reply_markup=ReplyKeyboardRemove())
        await state.set_state(AdminStatementRegForm.code)
    else:
        await unknown_func(message)

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

@router.message(AdminStatementRegForm.code)
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
                confirm = row[7]
                username = row[3]
                user_id = row[2]
                voice_id = row[6]
                photo_id = row[5]
                count_row += 1

            if count_row != 0:
               
                if confirm == 1:
                    await message.answer("Это заявление уже зарегестрированно", reply_markup=ReplyKeyboardRemove())
                elif confirm == 3:
                    await message.answer("Это согласование отклонено", reply_markup=ReplyKeyboardRemove())
                elif confirm == 3:
                    await message.answer("Это согласование отклонено", reply_markup=ReplyKeyboardRemove())
                elif not username: 
                    await message.answer("Ни один ученик еще не заполнил это заявление", reply_markup=ReplyKeyboardRemove())
                elif confirm == 4:
                    await state.update_data(code=message.text)
                    conf_text = (
                        f'<u>Заявление: {message.text}</u>'
                        f'\nДля связи: @{username}'
                    )                
                    await message.answer(conf_text)
                    
                    await bot.send_photo(message.from_user.id, photo_id)
                    await bot.send_voice(message.from_user.id, voice_id)

                    await state.set_state(AdminStatementRegForm.reg_num)
                    await message.answer("Введите регистрационный номер заявления", reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer("Такого кода заявления не существует.", reply_markup=ReplyKeyboardRemove())

            cnx.close()
    except Exception as e:
        print(e)
        await wrong(message)

@router.message(AdminStatementRegForm.reg_num)
async def reg_num_enter(message: Message, state: FSMContext) -> None:
    await state.update_data(reg_num=message.text)
    await state.set_state(AdminStatementRegForm.confirm)

    await message.answer(
    'Выберите действие',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Готово")
                ],
                [
                    KeyboardButton(text="Отменить")
                ]
            ],
            resize_keyboard=True,
        ),
    )

@router.message(AdminStatementRegForm.confirm, F.text.casefold() == "готово")
async def application_process_send(message: Message, state: FSMContext) -> None: 
    try:
        cnx = sql_conf.mysql_create()
        data = await state.get_data()
        await state.clear()

        code = data['code']
        reg_num = data['reg_num']
        
        check_guest_query = (f"UPDATE statements_bucket SET "
                                                f"confirm = 1, number = '{reg_num}' "                                               
                                                f"WHERE code = '{code}'")
        
        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            cnx.commit()

        next_message = (
            f"<u>Согласование {code}</u>\n"
            f"Зарегестрированно"
        )
        await message.answer(next_message, reply_markup=ReplyKeyboardRemove())

        cnx.close()
        #отправляем уведомление на согласование
    except Exception as e:
        print(e)
        await wrong(message)