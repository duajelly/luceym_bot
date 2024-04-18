import sql_conf

from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import Router

from handlers.main import unknown_func
from admin_handlers.access_groups import STATEMENT_REG_ADMIN

router = Router()

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["all_unclosed_statements_reg"]))
async def start(message: Message) -> None:
    if message.from_user.id == STATEMENT_REG_ADMIN:
            try:
                cnx = sql_conf.mysql_create()

                close_application_query = (f"SELECT * FROM statements_bucket WHERE confirm = 4 AND username IS NOT NULL")                
                with cnx.cursor() as cursor:
                    cursor.execute(close_application_query)
                    result = cursor.fetchall()

                    count_row = 0
                    events_message = ['<b><u>Незакрытые дела:</u></b>']

                    for row in result:
                        count_row += 1
                        events_message.append(f'{count_row}. {row[0]} ')

                    if count_row == 0:
                        await message.answer("Нет заявлений", reply_markup=ReplyKeyboardRemove())
                    else:
                        await message.answer(str('\n'.join(events_message)))

            except Exception as e:
                print(e)
                await message.answer(f"Что то пошло не так. Проверьте код заявления или повторите попытку позже.", reply_markup=ReplyKeyboardRemove())
    else:
        await unknown_func(message)