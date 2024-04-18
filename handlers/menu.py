from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram import Router
import sql_conf
from analytics import send_analytics
from handlers.main import sth_wrong as wrong
from config import bot

from aiogram3_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar

router = Router()

class MenuForm(StatesGroup):
    date = State()

@router.message(Command(commands=['menu']))
async def send_welcome(message: Message, state: FSMContext) -> None:     

    await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='menu')

    await message.answer("На какой день ты хочешь знать меню?", reply_markup=await SimpleCalendar().start_calendar())  
    await state.set_state(MenuForm.date)

@router.callback_query(simple_cal_callback.filter(), MenuForm.date)
async def select_time(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)

    if selected:
        date = "menu_" + date.strftime("%d-%m-%Y")
        
        try:
            cnx = sql_conf.mysql_create()
            event_query = (f"SELECT * FROM documents_bucket WHERE name = '{date}'")

            with cnx.cursor() as cursor:
                cursor.execute(event_query)
                result = cursor.fetchall()            
                
                i=0
                for row in result:
                    file_id = row[0]
                    i+=1
                
                if i:
                    await bot.delete_message(message_id=callback_query.message.message_id, chat_id=callback_query.from_user.id)
                    await bot.send_document(callback_query.from_user.id, file_id)
                else:
                    await bot.delete_message(message_id=callback_query.message.message_id, chat_id=callback_query.from_user.id)
                    await bot.send_message(callback_query.from_user.id, "Админы не загрузили меню на этот день")
                
                await state.clear()
        except Exception as e:
            wrong(callback_query.message, e)