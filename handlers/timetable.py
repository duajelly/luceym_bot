from aiogram.types.input_file import InputFile, FSInputFile
from aiogram import Router
from aiogram import types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters import Text
import sql_conf
from config import bot
from analytics import send_analytics
from handlers.main import sth_wrong as wrong

import time, os
os.environ['TZ'] = 'Asia/Yekaterinburg'

router = Router()

@router.message(Command(commands=['timetable']))
async def send_welcome(message: Message) -> None:   

    buttons = [
        [types.InlineKeyboardButton(text="8 и 9А класс", callback_data="timetable_list_1")],
        [types.InlineKeyboardButton(text="9Б и 10А класс", callback_data="timetable_list_2")],
        [types.InlineKeyboardButton(text="10Б и 11А класс", callback_data="timetable_list_3")],
        [types.InlineKeyboardButton(text="11Б и 11В класс", callback_data="timetable_list_4")],
        [types.InlineKeyboardButton(text="Отменить", callback_data="cancel_timetable")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)

    new_message = (
        f'Выбери для какого класса тебе нужно расписание'
    )
    await message.answer(new_message, reply_markup=keyboard)

@router.callback_query(Text(text=["cancel_timetable"]))
async def cancel_handler_query(query: types.CallbackQuery) -> None:
    await query.answer('')
    await bot.edit_message_text(text=f"Отменено", message_id=query.message.message_id, chat_id=query.from_user.id,reply_markup=None)

@router.callback_query(Text(text="timetable_list_1"))
async def send_timetable_1(query: types.CallbackQuery):
    await send_analytics(user_id=query.from_user.id,
                        user_lang_code=query.from_user.language_code,
                        action_name='timetable_list_1')
    await query.answer('')

    try:
        cnx = sql_conf.mysql_create()
        event_query = (f"SELECT * FROM documents_bucket WHERE name = 'timetable_list_1'")


        with cnx.cursor() as cursor:
            cursor.execute(event_query)
            result = cursor.fetchall()            

            for row in result:
                file_id = row[0]

        await bot.delete_message(message_id=query.message.message_id, chat_id=query.from_user.id)
        await bot.send_photo(query.from_user.id, file_id)                        
        
    except Exception as e:
        await wrong(query.message, e)

@router.callback_query(Text(text="timetable_list_2"))
async def send_timetable_2(query: types.CallbackQuery):
    await send_analytics(user_id=query.from_user.id,
                    user_lang_code=query.from_user.language_code,
                    action_name='timetable_list_2')
    await query.answer('')

    try:
        cnx = sql_conf.mysql_create()
        event_query = (f"SELECT * FROM documents_bucket WHERE name = 'timetable_list_2'")

        with cnx.cursor() as cursor:
            cursor.execute(event_query)
            result = cursor.fetchall()            

            for row in result:
                file_id = row[0]

        await bot.delete_message(message_id=query.message.message_id, chat_id=query.from_user.id)
        await bot.send_photo(query.from_user.id, file_id)                        
        
    except Exception as e:
        await wrong(query.message, e)

@router.callback_query(Text(text="timetable_list_3"))
async def send_timetable_3(query: types.CallbackQuery):
    await send_analytics(user_id=query.from_user.id,
                user_lang_code=query.from_user.language_code,
                action_name='timetable_list_3')
    await query.answer('')

    try:
        cnx = sql_conf.mysql_create()
        event_query = (f"SELECT * FROM documents_bucket WHERE name = 'timetable_list_3'")

        with cnx.cursor() as cursor:
            cursor.execute(event_query)
            result = cursor.fetchall()            

            for row in result:
                file_id = row[0]

        await bot.delete_message(message_id=query.message.message_id, chat_id=query.from_user.id)
        await bot.send_photo(query.from_user.id, file_id)                        
        
    except Exception as e:
        await wrong(query.message, e)

@router.callback_query(Text(text="timetable_list_4"))
async def send_timetable_4( query: types.CallbackQuery):
    await send_analytics(user_id=query.from_user.id,
                user_lang_code=query.from_user.language_code,
                action_name='timetable_list_4')
    await query.answer('')
    
    try:
        cnx = sql_conf.mysql_create()
        event_query = (f"SELECT * FROM documents_bucket WHERE name = 'timetable_list_4'")

        with cnx.cursor() as cursor:
            cursor.execute(event_query)
            result = cursor.fetchall()            

            for row in result:
                file_id = row[0]

        await bot.delete_message(message_id=query.message.message_id, chat_id=query.from_user.id)
        await bot.send_photo(query.from_user.id, file_id)                        
        
    except Exception as e:
        await wrong(query.message, e)