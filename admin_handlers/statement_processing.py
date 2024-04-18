import datetime as dt
import time, os
os.environ['TZ'] = 'Asia/Yekaterinburg'

from config import bot
import sql_conf
from handlers.main import sth_wrong as wrong
from handlers.main import unknown_func
from admin_handlers.access_groups import STATEMENT_REG_ADMIN, STATEMENT_ADMIN

from aiogram.types import Message
from aiogram.filters import Command, CommandObject, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram import F, Router, types, html

router = Router()

class AdminStatementForm(StatesGroup):
    code = State()
    confirm = State()    

router = Router()

@router.message(Command(commands=['close_statement']))
async def start(message: Message, state: FSMContext) -> None:
    if message.from_user.id == STATEMENT_ADMIN:       
        await message.answer("Введите код заявления",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Отменить")
                        ]
                    ],
                    resize_keyboard=True,
                ))
        await state.set_state(AdminStatementForm.code)
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

@router.message(AdminStatementForm.code)
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
                number = row[1]                
                date = time.strftime('%d.%m.%y', time.gmtime(row[4]))
                count_row += 1

            if count_row != 0:
               
                if confirm == 1 and number:
                    await message.answer(f"Вы уже подтвердили этот выезд\nРегистрация №{number}\nот {date}", reply_markup=ReplyKeyboardRemove())
                elif confirm == 1 and not number:
                    await message.answer(f"Вы уже подтвердили этот выезд\nБез требования регистрации", reply_markup=ReplyKeyboardRemove())
                elif confirm == 4:
                    await message.answer("Вы уже подтвердили этот выезд.\n Заявление в процессе регистрации.", reply_markup=ReplyKeyboardRemove())
                elif confirm == 3:
                    await message.answer("Это согласование отклонено", reply_markup=ReplyKeyboardRemove())
                elif not username: 
                    await message.answer("Ни один ученик еще не заполнил это заявление", reply_markup=ReplyKeyboardRemove())
                else:
                    await state.update_data(code=message.text)
                    conf_text = (
                        f'<u>Заявление: {message.text}</u>'
                        f'\nДля связи: @{username}'
                    )                
                    await message.answer(conf_text)
                    
                    await bot.send_photo(message.from_user.id, photo_id)
                    await bot.send_voice(message.from_user.id, voice_id)

                    await state.set_state(AdminStatementForm.confirm)
                    await message.answer(
                        'Вынесите вердикт.',
                            reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [
                                        KeyboardButton(text="Подтвердить"),
                                        KeyboardButton(text="Отклонить")
                                    ],
                                    [
                                        KeyboardButton(text="Отправить на ргистрацию")
                                    ],
                                    [
                                        KeyboardButton(text="Отменить")
                                    ]
                                ],
                                resize_keyboard=True,
                            )
                        )
            else:
                await message.answer("Такого кода заявления не существует.", reply_markup=ReplyKeyboardRemove())

            cnx.close()
    except Exception as e:
        print(e)
        await wrong(message)


@router.message(AdminStatementForm.confirm, F.text.casefold() == "отклонить")
async def application_process_cancel(message: Message, state: FSMContext) -> None:
    try:
        cnx = sql_conf.mysql_create()
        data = await state.get_data()
        await state.clear()

        code = data['code']
        
        check_guest_query = (f"UPDATE statements_bucket SET confirm = 3 "                                             
                                                f"WHERE code = '{code}'")
        
        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            cnx.commit()

        next_message = (
            f"<u>Согласование {code}</u>\n"
            f"Отклонено"
        )
        await message.answer(next_message, reply_markup=ReplyKeyboardRemove())
        await bot.send_message(user_id, f"Заявление {code} отклонено.")
        cnx.close()
        #отправляем уведомление на согласование
    except Exception as e:
        print(e)
        await wrong(message)

@router.message(AdminStatementForm.confirm, F.text.casefold() == "подтвердить")
async def application_process_send(message: Message, state: FSMContext) -> None: 
    try:
        cnx = sql_conf.mysql_create()
        data = await state.get_data()
        await state.clear()

        code = data['code']
        
        check_guest_query = (f"UPDATE statements_bucket SET "
                                                f"confirm = 1 "                                               
                                                f"WHERE code = '{code}'")
        
        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            cnx.commit()

        next_message = (
            f"<u>Согласование {code}</u>\n"
            f"Подтверждено. Без требования регистрации."
        )
        await message.answer(next_message, reply_markup=ReplyKeyboardRemove())
        await bot.send_message(user_id, f"Завяление {code} согласовано.\nРегистрация не требуется.", reply_markup=ReplyKeyboardRemove())
        cnx.close()
        #отправляем уведомление на согласование
    except Exception as e:
        print(e)
        await wrong(message)

@router.message(AdminStatementForm.confirm, F.text.casefold() == "отправить на ргистрацию")
async def application_process_send(message: Message, state: FSMContext) -> None: 
    try:
        cnx = sql_conf.mysql_create()
        data = await state.get_data()
        await state.clear()

        code = data['code']
        
        check_guest_query = (f"UPDATE statements_bucket SET "
                                                f"confirm = 4 "                                               
                                                f"WHERE code = '{code}'")
        
        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            cnx.commit()

        next_message = (
            f"<u>Согласование {code}</u>\n"
            f"Подтверждено, ожидание регистрации"
        )
        await message.answer(next_message, reply_markup=ReplyKeyboardRemove())
        await bot.send_message(user_id, f"Завяление {code} согласовано. В очереди на регистрацию.", reply_markup=ReplyKeyboardRemove())

        await bot.send_message(STATEMENT_REG_ADMIN, f"Завяление {code}. В очереди на регистрацию.", reply_markup=ReplyKeyboardRemove())
        cnx.close()
        #отправляем уведомление на согласование
    except Exception as e:
        print(e)
        await wrong(message)