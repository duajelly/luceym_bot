import datetime as dt
import time, os
# os.environ['TZ'] = 'Asia/Yekaterinburg'

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

class AdminEventForm(StatesGroup):
    title = State()
    date = State()
    time = State()

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["add_event"]))
async def start_add_event(message: Message, state: FSMContext) -> None:
    if message.from_user.id in EVENT_ACCESS:

        await message.answer("Функция добавления мероприятия в список.\n Для отмены на любом этапе /cancel", reply_markup=ReplyKeyboardRemove())
        await message.answer('Введите название мероприятия', reply_markup=ReplyKeyboardRemove())
        
        await state.set_state(AdminEventForm.title)
    else:
        await unknown_func(message)

@router.message(AdminEventForm.title)
async def select_date(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(AdminEventForm.date)

    await message.answer("Введите дату проведения ", reply_markup=await SimpleCalendar().start_calendar())

@router.callback_query(simple_cal_callback.filter(), AdminEventForm.date)
async def select_time(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        await callback_query.message.answer(
            f'Вы выбрали: {date.strftime("%d-%m-%Y")}',
            reply_markup=None
        )

        await state.update_data(date=date.strftime("%d-%m-%Y"))
        await state.set_state(AdminEventForm.time)
        await callback_query.message.answer('Введите время проведения в формате <b>чч мм</b>', reply_markup=None)

@router.message(AdminEventForm.time)
async def confirm_datetime(message: Message, state: FSMContext) -> None:
    await state.update_data(time=message.text)
  
    data = await state.get_data()
    await state.clear()

    try:
        global title, unix_time
        title, date, time = data['title'], data['date'], data['time']

        time = time.replace(' ', ":")

        unix_time = int(dt.datetime.strptime(str(date + " " + time), '%d-%m-%Y %H:%M').timestamp()) + 18000

        confirm_message = (
            f'Название мероприятия {title}'
            f'\nДата и время: {date} {time}'
        )

        await message.answer(confirm_message, reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Отправить"),
                            KeyboardButton(text="Изменить"),
                            KeyboardButton(text="Отменить"),
                        ]
                    ],
                    resize_keyboard=True
                )
            )
    except Exception as e: 
        print(e)
        await message.answer("Вы ввели дату или время неверно. Повторите попытку.", reply_markup=ReplyKeyboardRemove())

@router.message(F.text.casefold() == "отправить")
async def application_process_send(message: Message, state: FSMContext) -> None: 

    try:
        cnx = sql_conf.mysql_create()        
        event_add_query = (f"INSERT INTO events_bucket (title, date) VALUES ('{title}', '{unix_time}')")
            
        with cnx.cursor() as cursor:
            cursor.execute(event_add_query)
            cnx.commit()

        del_events_query = (f"DELETE FROM events_bucket WHERE date < {int(time.time())+18000}")

        with cnx.cursor() as cursor:
            cursor.execute(del_events_query)
            cnx.commit()
        
        await message.answer("Мероприятие добавлено в список. Старые мероприятия были очищены. Для посмотра списка /events", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        print(e)
        await wrong(message, e, bot)

@router.message(Text(text=["отменить"], ignore_case=True))
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