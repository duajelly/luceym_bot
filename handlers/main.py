from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Router
import sql_conf
from config import bot

from admin_handlers.access_groups import ALL_ADMINS
from analytics import send_analytics
import logging
logging.basicConfig(format='%(asctime)s - %(process)d-%(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')

router = Router()

@router.message(Command(commands=['help_admin']))
async def admin_send_welcome(message: Message) -> None: 
    if message.from_user.id in ALL_ADMINS:

        welcome_message = (
            '/add_event - добавить мероприятие'
            '\n/set_timetable - установить расписание'
            '\n/set_menu - установить меню'  
            '\n/generate - сгенерировать заявления'            

            '\n\n<u>Здорик АС</u>'
            '\n/close_statement - администрирование выездов'
            '\n/all_unclosed_statements_admin - неподтвержденные выезды'

            '\n\n<u>Эберляйн МВ</u>'
            '\n/application_close - закрыть заявку на справку'
            '\n/all_applications - все заявки на справку'
            '\n/statement_reg- зарегестрировать выезд'
            '\n/all_unclosed_statements_reg - незарегестрированные выезды'
        )
        await message.answer(welcome_message, reply_markup=ReplyKeyboardRemove())
    else: 
        await message.answer("Не дорос еще!", reply_markup=ReplyKeyboardRemove()) 
    
@router.message(Command(commands=['start', 'help']))
async def send_welcome(message: Message, state: FSMContext) -> None:
    await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='start')              
    
    exec('try: name = message.chat.first_name\nexcept:name = "Человек"')

    welcome_message = (
        f'Привет, {message.from_user.first_name}! 🤚'
        'Это бот "Территории сосен" и вот как я могу тебе помочь:'
        '\n\n<b></b> /timetable  - актуальное расписание уроков'
        '\n<b></b> /events  - ближайшие мероприятия'
        '\n<b></b> /statement - согласовать завяление на выезд'
        '\n<b></b> /document - заявка на получение справки об обучении в ОУ'    
        #'\n<b>[dev]</b> /trips - совместные поездки'    
        '\n<b></b> /menu - меню в столовой'
        '\n<b>[dev]</b> /question - задать вопрос администрации'
        '\n\nТы можешь подписаться на рассылку для того, чтобы получать сообщения с актуальной информацией от администрации. Просто напиши мне /subscribe 😉'
    )
    await message.answer(welcome_message, reply_markup=ReplyKeyboardRemove())

    await message.answer('\n\n<i>Внимание, продолжая использование, ты даёшь '
                         'согласие на сбор и обработку личных данных (Фамилия,'
                         ' Имя, Отчество, Класс), в том числе на возможное связывание '
                         'этих данных с информацией о посещениях данного приложения, '
                         'которую собирает Google Аналитика. Подробнее support@sipgc.ru</i>')

    try:
        cnx = sql_conf.mysql_create()
        check_guest_query = (f"SELECT * FROM users_bucket where id='{message.from_user.id}'")
        
        with cnx.cursor() as cursor:
            cursor.execute(check_guest_query)
            result = cursor.fetchall()

            count = 0
            for row in result:
                count += 1

            if count == 0:
                check_guest_query = (f"INSERT INTO users_bucket (id, username, subscription) VALUES ('{message.from_user.id}', '{message.from_user.username}', 0)")

                cursor.execute(check_guest_query)
                cnx.commit()
        cnx.close()

    except Exception as e:
        print(e)

# @router.message(F.content_type.in_({'voice'}))
# async def handle_text(message: Message) -> None:
#     file_id = message.voice.file_id
#     file = await bot.get_file(file_id)
#     file_path = file.file_path
#     await bot.download_file(file_path, f"src/voice/{file_id}.mp3")

# @router.message(F.content_type.in_({'video_note'}))
# async def handle_text(message: Message) -> None:
#     await message.answer(str(message))

# @router.message(F.content_type.in_({'photo'}))
# async def handle_text(message: Message) -> None:
#     await bot.download(
#         message.photo[-1],
#         destination=f"src/img/{message.photo[-1].file_id}.jpg"
#     )
#     photo=open(f"src/img/{message.photo[-1].file_id}.jpg", "rb")
#     await bot.send_photo(message.from_user.id, photo)

@router.message()
async def unknown_func(message: Message) -> None:
    await message.answer("Я не знаю такую команду. Что бы я рассказал тебе о своих функциях напиши /help",  reply_markup=ReplyKeyboardRemove())

async def sth_wrong (message: Message, e) -> None:
    await send_analytics(user_id=message.from_user.id,
                        user_lang_code=message.from_user.language_code,
                        action_name='error')
    logging.warning(e)
    await message.answer("Что то пошло не так. Я уже сообщил об этом админам", reply_markup=ReplyKeyboardRemove())