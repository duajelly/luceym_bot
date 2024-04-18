import datetime as dt
import time, os
os.environ['TZ'] = 'Asia/Yekaterinburg'

import sql_conf
from admin_handlers.access_groups import EVENT_ACCESS

from aiogram.types import Message
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from aiogram import F, Router
from handlers.main import sth_wrong as wrong
from handlers.main import unknown_func
from config import bot

from aiogram3_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

router = Router()

class AdminMenuForm(StatesGroup):
    date = State()
    file = State()

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["set_menu"]))
async def start_add_event(message: Message, state: FSMContext) -> None:
    if message.from_user.id in EVENT_ACCESS:
        await message.answer("Введите дату на которое хотите загрузить меню", reply_markup=await SimpleCalendar().start_calendar())
        await state.set_state(AdminMenuForm.date)
    else:
        await unknown_func(message)

@router.callback_query(simple_cal_callback.filter(), AdminMenuForm.date)
async def select_time(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        await callback_query.message.answer("Выбрана дата:" + str(date.strftime("%d-%m-%Y")))
        date = "menu_" + date.strftime("%d-%m-%Y")
        await state.update_data(date=date)
        await callback_query.message.answer("Загрузите файл с меню")
        await state.set_state(AdminMenuForm.file)

@router.message(AdminMenuForm.file, F.content_type.in_({'document'}))
async def select_date(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    try:
        check_guest_query = (f"INSERT INTO documents_bucket (file_id, name) VALUES ('{message.document.file_id}', '{data['date']}')")
        cnx = sql_conf.mysql_create() 

        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            cnx.commit()

        await bot.send_message(message.from_user.id, f"Лист меню {data['date']} обновлён", reply_markup=None)
        await state.clear()
    except Exception as e:
        await wrong(message, e)

@router.message(AdminMenuForm.file)
async def another(message: Message) -> None:
    await message.answer("Загрузите документ", reply_markup=None)
