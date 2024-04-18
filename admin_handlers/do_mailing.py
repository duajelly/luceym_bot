from config import bot
import sql_conf

from aiogram.types import Message
from aiogram.filters import Command, CommandObject, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram import F, Router, types, html

from handlers.main import unknown_func
from admin_handlers.access_groups import MAILING_ACCESS

router = Router()
global mailing_message

class AdminMailingForm(StatesGroup):
    text_typing = State()
    selecet_next_step = State()

#ожидаем когда пользователь введет команду для активации заполнения заявки
@router.message(Command(commands=["mailing"]))
async def start(message: Message, state: FSMContext) -> None:
    if message.from_user.id in MAILING_ACCESS:
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data="cancel")
        )

        global next_message
        next_message = (
            'Ниже введите текст рассылки. Форматирование текста будет сохранено.'
        )

        await message.answer(
                next_message, 
                reply_markup=builder.as_markup()
            )
        
        await state.set_state(AdminMailingForm.text_typing)
    else:
        await unknown_func(message)

#отмена заполнения
@router.callback_query(Text(text=["cancel"]), AdminMailingForm.text_typing)
async def cancel_handler_query(query: types.CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await query.answer('')
    await bot.send_message(query.from_user.id,
        "Отменено",
        reply_markup = ReplyKeyboardRemove(),
    )

@router.message(AdminMailingForm.text_typing)
async def start(message: Message, state: FSMContext) -> None:
    global mailing_message
    mailing_message = message.html_text
    next_message = '<u>Текст рассылки:</u>\n\n' +  message.html_text
    
    await message.answer(
            next_message,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Отправить"),
                        KeyboardButton(text="Изменить"),
                        KeyboardButton(text="Отменить"),
                    ]
                ],
                resize_keyboard=True,
            ),
        )

    await state.set_state(AdminMailingForm.selecet_next_step)
       

@router.message(AdminMailingForm.selecet_next_step, F.text.casefold() == "изменить")
async def application_process_edit(message: Message, state: FSMContext) -> None:
    await state.clear()
    await start(message, state)

@router.message(AdminMailingForm.selecet_next_step, F.text.casefold() == "отменить")
async def application_process_cancel(message: Message, state: FSMContext) -> None:
    await cancel_handler_query(message, state)

@router.message(AdminMailingForm.selecet_next_step, F.text.casefold() == "отправить")
async def application_process_send(message: Message, state: FSMContext) -> None: 

    await state.clear()

    await message.answer("Рассылка начата, ожидайте завершения.", reply_markup=ReplyKeyboardRemove())

    user_count = 0

    cnx = sql_conf.mysql_create()
    select_mailing_query = "SELECT * FROM users_bucket WHERE subscription = 1"

    with cnx.cursor() as cursor:
        cursor.execute(select_mailing_query)
        result = cursor.fetchall()
        for row in result:
            user_count += 1
            await bot.send_message(row[0], mailing_message)
    
    cnx.close()
            
    await message.answer(f"Рассылка завершена. Сообщение было отправлено {user_count} пользователям(ю)", reply_markup=ReplyKeyboardRemove())