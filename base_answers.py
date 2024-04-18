from aiogram.types import Message

async def denied(message: Message) -> None:
    welcome_message = (
        f'Не знаю такое.'        
    )
    await message.answer(welcome_message)