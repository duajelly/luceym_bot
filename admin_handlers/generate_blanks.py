from docxtpl import DocxTemplate
import random
import string
import datetime
import time
import sql_conf
from config import bot
from analytics import send_analytics
from handlers.main import sth_wrong as wrong
from handlers.main import unknown_func

from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Router

from admin_handlers.access_groups import GENERATE_ACCESS
router = Router()

@router.message(Command(commands=["generate"]))
async def start_generate(message: Message, state: FSMContext) -> None:
    if message.from_user.id in GENERATE_ACCESS:

        await send_analytics(user_id=message.from_user.id,
                            user_lang_code=message.from_user.language_code,
                            action_name='generation_blanks')

        await message.answer("Ожидайте, завяления генерируются")

        doc = DocxTemplate("src/docx/template.docx")

        try:
            global cnx, generation
            cnx = sql_conf.mysql_create()
            generation = time.time()
            mant = str(float(generation))[str(float(generation)).find('.')+1:]

            def generate_alphanum_random_string(length):
                global cnx, generation
                letters_and_digits = string.digits
                rand_string = ''.join(random.sample(letters_and_digits, length))

                check_guest_query = (f"INSERT INTO statements_bucket (code, generation) VALUES ('{rand_string}', '{generation}') ")

                with cnx.cursor() as cursor:
                    cursor.execute(check_guest_query)
                    cnx.commit()
            
                return rand_string

            now = datetime.datetime.now()
            context = { 
                    'code1' : generate_alphanum_random_string(5),
                    'code2' : generate_alphanum_random_string(5),
                    'code3' : generate_alphanum_random_string(5),
                    'code4' : generate_alphanum_random_string(5),
                    'code5' : generate_alphanum_random_string(5),
                    'code6' : generate_alphanum_random_string(5),
                    'code7' : generate_alphanum_random_string(5),
                    'code8' : generate_alphanum_random_string(5),
                    'code9' : generate_alphanum_random_string(5),
                    'code10' : generate_alphanum_random_string(5),
                    'code11' : generate_alphanum_random_string(5),
                    'code12' : generate_alphanum_random_string(5),
                    'generation' : f"*.{mant}" 
                    }
            doc.render(context)
            doc.save("src/docx/generated.docx")


            file = FSInputFile('./src/docx/generated.docx')

            await bot.send_document(message.from_user.id, file)

        except Exception as e:
            await wrong(message, e)
    else:
        await unknown_func(message)