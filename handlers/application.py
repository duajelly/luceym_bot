import sql_conf
from admin_handlers.access_groups import APPLICATION_ADMIN
from analytics import send_analytics

from handlers.main import sth_wrong as wrong
from config import bot

from aiogram.types import Message, KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router, types

import random
import string
import logging

router = Router()
global next_message
next_message = 0

class UserApplicationForm(StatesGroup):
    child_info = State()
    confirm = State()

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["document"]))
async def start(message: Message, state: FSMContext) -> None:

    if message.from_user.username == None:
        await message.answer("Тебе не доступна эта функция потому, что у тебя не установлено имя пользователя. Сделай это в настройках и возвращайся!")
    else:
        await send_analytics(user_id=message.from_user.id,
                            user_lang_code=message.from_user.language_code,
                            action_name='applications_start')
        
        global next_message
        next_message = (
            'Напиши твоё ФИО и класс одним сообщением '
            '\nНапример: Петров Пётр Петрович 8А'
        )

        await message.answer(next_message, reply_markup=ReplyKeyboardMarkup(
                                            keyboard=[[KeyboardButton(text="Отменить")]], resize_keyboard=True  
                                        ))
        
        await state.set_state(UserApplicationForm.child_info)

#отмена заполнения
@router.message(Command(commands=["cancel"]))
@router.message(F.text.casefold() == "отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup = ReplyKeyboardRemove(),
    )

#отмена заполнения
@router.callback_query(Text(text=["cancel"]), UserApplicationForm.child_info)
async def cancel_handler_query(query: types.CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await query.answer('')
    await bot.send_message(query.from_user.id,
        "Отменено",
        reply_markup = ReplyKeyboardRemove(),
    )

#следующий шаг после того как получили данные
@router.message(UserApplicationForm.child_info)
async def getChildInfo(message: Message, state: FSMContext) -> None:
    
    await state.update_data(child_info=message.text)
    await state.set_state(UserApplicationForm.confirm)

    try:
        global temp_child
        user_data = message.text
        temp_child = {
            "name": user_data.split()[1],
            "surname": user_data.split()[0], 
            "patronymic": user_data.split()[2], 
            "class": user_data.split()[3]
        }

        next_message_application_user = (
            '<b><u>Заявка на справку от ОУ</u></b>'
            f'\nФамилия: {temp_child["surname"]}'
            f'\nИмя: {temp_child["name"]}'
            f'\nОтчество: {temp_child["patronymic"]}'
            f'\nКласс: {temp_child["class"]}'
        )

        await message.answer(
            next_message_application_user,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Отправить"),
                        KeyboardButton(text="Изменить"),
                        KeyboardButton(text="Отменить"),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        
    except Exception as e:
        print(e)
        await start(message, state)

@router.message(UserApplicationForm.confirm, F.text.casefold() == "изменить")
async def application_process_edit(message: Message, state: FSMContext) -> None:
    await start(message, state)

@router.message(UserApplicationForm.confirm, F.text.casefold() == "отменить")
async def application_process_cancel(message: Message, state: FSMContext) -> None:
    await cancel_handler(message, state)

@router.message(UserApplicationForm.confirm, F.text.casefold() == "отправить")
async def application_process_send(message: Message, state: FSMContext) -> None:    
    try:

        def generate_alphanum_random_string(length):
            letters_and_digits = string.ascii_letters + string.digits
            rand_string = ''.join(random.sample(letters_and_digits, length))
            return rand_string        

        rand_str = generate_alphanum_random_string(5)

        try:         
            global temp_child
            cnx = sql_conf.mysql_create()
            check_guest_query = (f"INSERT INTO application_requests (user_id, hash, name, surname, patronymic, class) VALUES "
            f"('{message.from_user.id}', '{rand_str}', '{temp_child['name']}', '{temp_child['surname']}', '{temp_child['patronymic']}', '{str(temp_child['class'])}')")
            
            with cnx.cursor() as cursor:
                cursor.execute(check_guest_query)
                cnx.commit()

            next_message = (
                '<b><u>Заявка на справку от ОУ</u></b>'
                f'\nФамилия: {temp_child["surname"]}'
                f'\nИмя: {temp_child["name"]}'
                f'\nОтчество: {temp_child["patronymic"]}'
                f'\nКласс: {temp_child["class"]}'
                f'\nID-tg: {str(message.from_user.username)}'
                f'\nDelivery code: {rand_str}'
                '\nАдминистратору'
            )      
            await bot.send_message(APPLICATION_ADMIN, next_message, reply_markup=ReplyKeyboardRemove())

            await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='application_end')

            await message.answer('Заявка отправлена. Когда справка будет готова я сообщу тебе об этом. Обычно это просиходит в течение двух рабочих дней.',  reply_markup=ReplyKeyboardRemove())
            await state.clear()
            cnx.close()
        except Exception as e:
            await state.clear()
            await wrong(message, e)
    except Exception as e:
        await state.clear()
        await wrong(message, e)

@router.message(UserApplicationForm.confirm)
async def process_unknown_write_bots(message: Message) -> None:
    await message.reply("Я не понимаю тебя, воспользуйся кнопками!",  reply_markup=ReplyKeyboardRemove())