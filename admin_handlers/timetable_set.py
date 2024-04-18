import sql_conf

from aiogram.filters import Command, CommandObject, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram import F, Router, types
from config import bot

from admin_handlers.access_groups import EVENT_ACCESS
from handlers.main import sth_wrong as wrong
from handlers.main import unknown_func

import time, os
os.environ['TZ'] = 'Asia/Yekaterinburg'

router = Router()

class AdminTimeForm(StatesGroup):
    upload_files = State()
    
    timetable_chg_1 = State()
    timetable_chg_2 = State()
    timetable_chg_3 = State()
    timetable_chg_4 = State()

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["set_timetable"]))
async def start(message: Message) -> None:
    if message.from_user.id in EVENT_ACCESS:
        buttons = [
            [types.InlineKeyboardButton(text="Установить", callback_data="timetable_chg")],
            [types.InlineKeyboardButton(text="Upload (internal dev)", callback_data="upload_dev")],
            [types.InlineKeyboardButton(text="Cancel", callback_data="cancel")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Выберите комаду", reply_markup=keyboard)
    else:
        await unknown_func(message)

@router.callback_query(Text(text=["cancel"]))
async def cancel_handler_query(query: types.CallbackQuery, state: FSMContext) -> None:
    await query.answer('')
    await state.clear()
    await bot.edit_message_text(text=f"Отменено", message_id=query.message.message_id, chat_id=query.from_user.id,reply_markup=None)

@router.callback_query(Text(text="timetable_chg"))
async def start_upload_id(query: types.CallbackQuery):
    if query.from_user.id in EVENT_ACCESS:
        await query.answer('')

        buttons = [
            [types.InlineKeyboardButton(text="Лист 1", callback_data="timetable_chg_1")],
            [types.InlineKeyboardButton(text="Лист 2", callback_data="timetable_chg_2")],
            [types.InlineKeyboardButton(text="Лист 3", callback_data="timetable_chg_3")],
            [types.InlineKeyboardButton(text="Лист 4", callback_data="timetable_chg_4")],
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.edit_message_text(text=f"Введите выберите лист для изменения", message_id=query.message.message_id, chat_id=query.from_user.id,reply_markup=keyboard)

#лист 1
@router.callback_query(Text(text="timetable_chg_1"))
async def selected_list_1(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id in EVENT_ACCESS:
        await query.answer('')

        buttons = [
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await bot.edit_message_text(text=f"Загрузите фотографию расписания (Лист 1)", message_id=query.message.message_id, chat_id=query.from_user.id,reply_markup=keyboard)
        await state.set_state(AdminTimeForm.timetable_chg_1)

@router.message(F.content_type.in_({'document'}), AdminTimeForm.timetable_chg_1)
async def photo_err(message: Message, state: FSMContext) -> None:
    await message.answer('Пожалуйста, приложите изображение (c сжатием), а не как файл.')

@router.message(AdminTimeForm.timetable_chg_1)
async def upload_list_1 (message: Message, state: FSMContext) -> None:
    if message.from_user.id in EVENT_ACCESS:
        try:
            check_guest_query = (f"UPDATE documents_bucket SET file_id = '{message.photo[-1].file_id}'"
                                                    f" WHERE name = 'timetable_list_1'")
            cnx = sql_conf.mysql_create() 

            with cnx.cursor() as cursor:
                cursor.execute(check_guest_query)
                cnx.commit()

            await bot.send_message(message.from_user.id, f"Лист 1 обновлён", reply_markup=None)
            await state.clear()
        except Exception as e:
            print(e)
            await wrong(message)


#лист 2
@router.callback_query(Text(text="timetable_chg_2"))
async def selected_list_1(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id in EVENT_ACCESS:
        await query.answer('')

        buttons = [
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await bot.edit_message_text(text=f"Загрузите фотографию расписания (Лист 2)", message_id=query.message.message_id, chat_id=query.from_user.id,reply_markup=keyboard)
        await state.set_state(AdminTimeForm.timetable_chg_1)

@router.message(F.content_type.in_({'document'}), AdminTimeForm.timetable_chg_2)
async def photo_err(message: Message, state: FSMContext) -> None:
    await message.answer('Пожалуйста, приложите изображение (c сжатием), а не как файл.')

@router.message(AdminTimeForm.timetable_chg_1)
async def upload_list_1 (message: Message, state: FSMContext) -> None:
    if message.from_user.id in EVENT_ACCESS:
        try:
            check_guest_query = (f"UPDATE documents_bucket SET file_id = '{message.photo[-1].file_id}'"
                                                    f" WHERE name = 'timetable_list_2'")
            cnx = sql_conf.mysql_create() 

            with cnx.cursor() as cursor:
                cursor.execute(check_guest_query)
                cnx.commit()

            await bot.send_message(message.from_user.id, f"Лист 2 обновлён", reply_markup=None)
            await state.clear()
        except Exception as e:
            print(e)
            await wrong(message)


#лист 3
@router.callback_query(Text(text="timetable_chg_3"))
async def selected_list_1(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id in EVENT_ACCESS:
        await query.answer('')

        buttons = [
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await bot.edit_message_text(text=f"Загрузите фотографию расписания (Лист 3)", message_id=query.message.message_id, chat_id=query.from_user.id,reply_markup=keyboard)
        await state.set_state(AdminTimeForm.timetable_chg_1)

@router.message(F.content_type.in_({'document'}), AdminTimeForm.timetable_chg_3)
async def photo_err(message: Message, state: FSMContext) -> None:
    await message.answer('Пожалуйста, приложите изображение (c сжатием), а не как файл.')

@router.message(AdminTimeForm.timetable_chg_1)
async def upload_list_1 (message: Message, state: FSMContext) -> None:
    if message.from_user.id in EVENT_ACCESS:
        try:
            check_guest_query = (f"UPDATE documents_bucket SET file_id = '{message.photo[-1].file_id}'"
                                                    f" WHERE name = 'timetable_list_3'")
            cnx = sql_conf.mysql_create() 

            with cnx.cursor() as cursor:
                cursor.execute(check_guest_query)
                cnx.commit()

            await bot.send_message(message.from_user.id, f"Лист 3 обновлён", reply_markup=None)
            await state.clear()
        except Exception as e:
            print(e)
            await wrong(message)


#лист 4
@router.callback_query(Text(text="timetable_chg_4"))
async def selected_list_1(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id in EVENT_ACCESS:
        await query.answer('')

        buttons = [
            [types.InlineKeyboardButton(text="Отмена", callback_data="cancel")]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

        await bot.edit_message_text(text=f"Загрузите фотографию расписания (Лист 4)", message_id=query.message.message_id, chat_id=query.from_user.id,reply_markup=keyboard)
        await state.set_state(AdminTimeForm.timetable_chg_1)

@router.message(F.content_type.in_({'document'}), AdminTimeForm.timetable_chg_4)
async def photo_err(message: Message, state: FSMContext) -> None:
    await message.answer('Пожалуйста, приложите изображение (c сжатием), а не как файл.')

@router.message(AdminTimeForm.timetable_chg_1)
async def upload_list_1 (message: Message, state: FSMContext) -> None:
    if message.from_user.id in EVENT_ACCESS:
        try:
            check_guest_query = (f"UPDATE documents_bucket SET file_id = '{message.photo[-1].file_id}'"
                                                    f" WHERE name = 'timetable_list_4'")
            cnx = sql_conf.mysql_create() 

            with cnx.cursor() as cursor:
                cursor.execute(check_guest_query)
                cnx.commit()

            await bot.send_message(message.from_user.id, f"Лист 4 обновлён", reply_markup=None)
            await state.clear()
        except Exception as e:
            print(e)
            await wrong(message)


@router.callback_query(Text(text="upload_dev"))
async def start_upload_id(query: types.CallbackQuery, state: FSMContext):
    if query.from_user.id in EVENT_ACCESS:
        await query.answer('')
        await bot.send_message(query.from_user.id, "Заргружайте фотографии, в ответ будет выводиться file_id. После окончания напишите cancel")

        await state.set_state(AdminTimeForm.upload_files)

@router.message(AdminTimeForm.upload_files)
async def upload_file_id(message: Message, state: FSMContext):
    if message.from_user.id in EVENT_ACCESS:
        await message.answer(message.photo[-1].file_id)