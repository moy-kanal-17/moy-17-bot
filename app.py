import aiogram
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
import asyncio

# Token va Admin ID
TOKEN = '7838778700:AAE7HIfFvQUmx3ngdAvr6r-RrftM-D1OAC4'
ADMIN_ID = 5655572400  # O'zingizning Telegram ID ni shu yerga qo‘ying

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# /start komandasi
@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("🎬 Привет! Это бот для отбора в фильм. Просто отправьте своё фото!")

# /finish komandasi
@router.message(Command("finish"))
async def finish_command(message: types.Message):
    await message.answer("ТЫ ЕБЛАН УЖЕ УХОДИШ!")

# Oddiy matn xabarlarini qabul qilish
@router.message(lambda message: message.text is not None)
async def handle_text(message: types.Message):
    user_info = f"📩 Новое сообщение!\n👤 Имя: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}"
    if message.from_user.username:
        user_info += f"\n🔗 Username: @{message.from_user.username}"
    user_info += f"\n\n💬 Сообщение: {message.text}"

    await bot.send_message(ADMIN_ID, user_info)

# Rasmni qabul qilish va adminga jo‘natish
@router.message(lambda message: message.photo is not None)
async def handle_photo(message: types.Message):
    photo = message.photo[-1].file_id  # Eng katta sifatdagi rasmni olish
    caption = f"🖼 Новое фото!\n👤 Имя: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}"
    if message.from_user.username:
        caption += f"\n🔗 Username: @{message.from_user.username}"
    if message.caption:
        caption += f"\n✏️ Описание: {message.caption}"

    await bot.send_photo(ADMIN_ID, photo, caption=caption)

# Fayl jo‘natish (videolar va boshqa fayllar)
@router.message(lambda message: message.document is not None or message.video is not None)
async def handle_files(message: types.Message):
    caption = f"📂 Новый файл!\n👤 Имя: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}"
    if message.from_user.username:
        caption += f"\n🔗 Username: @{message.from_user.username}"
    if message.caption:
        caption += f"\n✏️ Описание: {message.caption}"

    if message.document:
        await bot.send_document(ADMIN_ID, message.document.file_id, caption=caption)
    elif message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption=caption)

# Routerni qo‘shish
dp.include_router(router)

# Botni ishga tushirish
async def on_start():
    print("✅ Bot ishga tushdi! 🎬")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(on_start())
