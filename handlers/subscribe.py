from config import bot
import sql_conf

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.types import  Message
from aiogram import Router
from analytics import send_analytics
from handlers.main import sth_wrong as wrong

router = Router()
global next_message
next_message = 0

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["subscribe"]))
async def start(message: Message) -> None:
    if message.from_user.username == None:
        await message.answer("Тебе не доступна эта функция потому, что у тебя не установлено имя пользователя. Сделай это в настройках и возвращайся!")
    else:
        try:
            cnx = sql_conf.mysql_create()

            check_guest_query = (f"UPDATE users_bucket SET subscription = 1 WHERE  id='{message.from_user.id}'")

            with cnx.cursor() as cursor:
                cursor.execute(check_guest_query)
                cnx.commit()

            await message.answer('Вы подписались на рассылку! Для того что бы отписаться /unsubscribe', reply_markup=ReplyKeyboardRemove())
            cnx.close()
            await send_analytics(user_id=message.from_user.id,
                            user_lang_code=message.from_user.language_code,
                            action_name='subscribe')
        except Exception as e:
            await wrong(message, e)

@router.message(Command(commands=["unsubscribe"]))
async def start(message: Message) -> None:
    try:
        cnx = sql_conf.mysql_create()
        check_guest_query = (f"UPDATE users_bucket SET subscription = 0 WHERE  id='{message.from_user.id}'")

        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            cnx.commit()

        await message.answer('Вы отписались от рассылки!', reply_markup=ReplyKeyboardRemove())  
        cnx.close()      

        await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='unsubscribe')
    except Exception as e: 
        await wrong(message, e)