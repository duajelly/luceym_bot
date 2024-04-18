import datetime as dt
import time, os
os.environ['TZ'] = 'Asia/Yekaterinburg'

from config import bot
import sql_conf
from handlers.main import sth_wrong as wrong
from admin_handlers.access_groups import STATEMENT_ADMIN
from analytics import send_analytics

from aiogram.types import Message, KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F, Router

router = Router()

class UserStatementForm(StatesGroup):
    code = State()
    terms = State()
    photo = State()
    reason = State()
    confirm = State()

router = Router()

@router.message(Command(commands=['statement']))
async def start(message: Message, state: FSMContext) -> None:
    if message.from_user.username == None:
        await message.answer("Тебе не доступна эта функция потому, что у тебя не установлено имя пользователя. Сделай это в настройках и возвращайся!")
    else:
        await send_analytics(user_id=message.from_user.id,
                            user_lang_code=message.from_user.language_code,
                            action_name='statement_start')
        
        # await message.answer("В бета-режиме доступно согласование у Здорик А.С. для 10ых классов", reply_markup=ReplyKeyboardRemove())
        await message.answer("Обрати внимание, что процесс согласования через бота может занимать до 24 часов после заполнения формы. Если тебе необходимо срочно согласовать выезд - лично обратись в администрацию.", reply_markup=ReplyKeyboardRemove())
        await message.answer("Введи уникальный пятизначный код, который указан на завялении. (Заявление нового образца)",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Отменить")
                    ]
                ],
                resize_keyboard=True
            ))     
        await state.set_state(UserStatementForm.code)

#отмена заполнения
@router.message(Command(commands=["cancel"]))
@router.message(F.text.casefold() == "отменить")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Нечего отменять",
            reply_markup = ReplyKeyboardRemove(),
    )
        return

    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup = ReplyKeyboardRemove(),
    )

@router.message(UserStatementForm.code)
async def photo_err(message: Message, state: FSMContext) -> None:
    try:
        cnx = sql_conf.mysql_create()
        event_query = (f"SELECT * FROM statements_bucket WHERE code = '{message.text}' AND username IS NULL AND user_id IS NULL")
        with cnx.cursor() as cursor:
            cursor.execute(event_query)
            result = cursor.fetchall()

            count_row = 0

            for row in result:
                count_row += 1
            
            if count_row:
                await state.update_data(code=message.text)
                await message.answer("Скинь мне фотографию заполненного завяления. Обязательно проследи за тем что бы все части заявления были различимы.",
                                    reply_markup=ReplyKeyboardMarkup(
                                        keyboard=[
                                            [
                                                KeyboardButton(text="Отменить")
                                            ]
                                        ],
                                        resize_keyboard=True
                                     ))
                await state.set_state(UserStatementForm.photo)

            else:
                await message.answer("Проверь введенный код. Заявление с таким кодом не существует, либо оно уже активировано.",
                                        reply_markup=ReplyKeyboardMarkup(
                                        keyboard=[[ KeyboardButton(text="Отменить")]],
                                        resize_keyboard=True))
        
        cnx.close()
    except Exception as e:
        await wrong(message,e)

@router.message(F.content_type.in_({'document'}), UserStatementForm.photo)
async def photo_err(message: Message, state: FSMContext) -> None:
    await message.answer('Пожалуйста, приложите изображение (c сжатием), а не как файл.')

@router.message(F.content_type.in_({'photo'}), UserStatementForm.photo)
async def step_photo(message: Message, state: FSMContext) -> None:
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(UserStatementForm.reason)
    # await bot.send_photo(message.from_user.id, message.photo[-1].file_id)

    next_message = (
        'Окей! Объясни свою причину выезда в голосовом сообщении и отправь его мне.\n'
        'Такой способ служит дополнительным методом подтверждения твоей личности.\n'
        'Помни: краткость - сестра таланта.\n'
        '\n '
    )
    await message.answer(next_message, reply_markup=None)

@router.message(UserStatementForm.photo)
async def photo_err(message: Message) -> None:
    await message.answer('Не знаю что ты имеешь в виду. Просто скинь мне фотографию твоего заявления.')

@router.message(F.content_type.in_({'voice'}), UserStatementForm.reason)
async def voce(message: Message, state: FSMContext) -> None:
    await state.update_data(reason=message.voice.file_id)
    await state.set_state(UserStatementForm.confirm)

    await message.answer(
       'Отлично! Подтверди отправку.',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[
                    KeyboardButton(text="Отправить"),
                    KeyboardButton(text="Отменить"),
            ]],
            resize_keyboard=True,
        )
    )

@router.message(UserStatementForm.reason)
async def voice_err(message: Message) -> None:
    await message.answer('Я не смогу передать это. Просто объясни все в коротком голосом сообщении.')

@router.message(UserStatementForm.confirm, F.text.casefold() == "изменить")
async def application_process_edit(message: Message, state: FSMContext) -> None:
    await state.set_state(UserStatementForm.code)
    await start(message)

@router.message(UserStatementForm.confirm, F.text.casefold() == "отменить")
async def application_process_cancel(message: Message, state: FSMContext) -> None:
    await cancel_handler(message, state)

@router.message(UserStatementForm.confirm, F.text.casefold() == "отправить")
async def application_process_send(message: Message, state: FSMContext) -> None: 
    try:
        data = await state.get_data()
        await state.clear()

        code, photo, voice = data['code'], data['photo'], data['reason']
        
        check_guest_query = (f"UPDATE statements_bucket SET "
                                                f"username = '{message.from_user.username}', "
                                                f"user_id = '{message.from_user.id}', "
                                                f"photo_id = '{photo}', "
                                                f"voice_id = '{voice}', "
                                                f"date = '{int(time.time())}'"
                                                f" WHERE code = '{code}'")
        cnx = sql_conf.mysql_create() 

        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            cnx.commit()

        next_message = (
            f"<u>Новое согласование {code}</u>\n"
        )
        await bot.send_message(STATEMENT_ADMIN, next_message)

        await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='statement_end')

        await message.answer("Твоя заявка успешно отправлена.\n\nТ.к. мы не храним файлы переписки на своих серверах, то я тебя прошу не удалять фотографию и голосовое сообщение до окончания процесса согласования.", reply_markup=ReplyKeyboardRemove())
        cnx.close()
        #отправляем уведомление на согласование
    except Exception as e:
        await wrong(message, e)