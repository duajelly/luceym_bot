import time, os
# os.environ['TZ'] = 'Asia/Yekaterinburg'
from analytics import send_analytics
from handlers.main import sth_wrong as wrong

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Router
import sql_conf

router = Router()

@router.message(Command(commands=['events']))
async def send_welcome(message: Message, state: FSMContext) -> None:            
    await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='events')
    try:
        cnx = sql_conf.mysql_create()
        event_query = (f"SELECT * FROM events_bucket WHERE date > {int(time.time()) + 18000}")
        with cnx.cursor() as cursor:
            cursor.execute(event_query)
            result = cursor.fetchall()

            count_row = 0

            events_message = ['<b><u>Ближайшие мероприятия:</u></b>']

            for row in result:
                count_row += 1
                my_time = time.strftime('%d.%m.%y %H:%M', time.gmtime(row[2]))
                events_message.append(f'{count_row}. {row[1]} {my_time}')

            if count_row == 0:
                await message.answer("Нет запланированных мероприятий", reply_markup=ReplyKeyboardRemove())
            else:
                await message.answer(str('\n'.join(events_message)), reply_markup=ReplyKeyboardRemove())
        
        cnx.close()
    except Exception as e:
        await wrong(message, e)