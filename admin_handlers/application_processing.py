import sql_conf

from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router
from config import bot

from handlers.main import unknown_func
from admin_handlers.access_groups import APPLICATION_ADMIN

router = Router()

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["application_close"]))
async def start(message: Message,  command: CommandObject) -> None:
    if message.from_user.id == APPLICATION_ADMIN:
        if command.args:
            try:
                try:
                    cnx = sql_conf.mysql_create()

                    split_data = str(command.args).split()
                        
                    close_application_query = (f"UPDATE application_requests SET is_ready=true WHERE hash='{split_data[0]}'")                
                    with cnx.cursor() as cursor:
                        cursor.execute(close_application_query)
                        cnx.commit()
                    
                except Exception as e:
                    print(e)  

                try:
                    select_userid_query = (f"SELECT * FROM application_requests where hash='{split_data[0]}'")                
                    with cnx.cursor() as cursor:
                        cursor.execute(select_userid_query)
                        result = cursor.fetchall()
                        for row in result:
                            userid = int(row[0])

                    if len(split_data) == 1:
                        await bot.send_message(int(userid), "Твоя справка готова, приходи за ней!", reply_markup=ReplyKeyboardRemove())
                        await message.answer(f"Закрыта заявка: {command.args}. Уведомление уведомление о готовности отправлено.", reply_markup=ReplyKeyboardRemove())
                    elif len(split_data) == 2 and split_data[1] == 'cancel':
                        await bot.send_message(int(userid), "Твоя заявка на получение справки от ОУ отклонена. Для получения подробной информации обращайся к специалисту.", reply_markup=ReplyKeyboardRemove())
                        await message.answer(f"Закрыта заявка: {split_data[0]}. Уведомление уведомление об <u>отмене</u> заявки отправлено.", reply_markup=ReplyKeyboardRemove())

                    cnx.close()                
                except Exception as e:
                    print(e)

            except Exception as e:
                print(e)
                await message.answer(f"Что то пошло не так. Проверьте D-code или повторите попытку позже.", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Введите D-code после команды в одном сообщении через пробел", reply_markup=ReplyKeyboardRemove())
    else:
        await unknown_func(message)