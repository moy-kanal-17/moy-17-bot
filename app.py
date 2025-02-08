import aiogram
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
import asyncio
import aiohttp
from g4f.client import Client  # GPT4Free kutubxonasi

TOKEN = '7838778700:AAE7HIfFvQUmx3ngdAvr6r-RrftM-D1OAC4'
ADMIN_ID = 5655572400
API_KEY = "0fd92f48fd3fbe6479333eeffdc1543c"

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
gpt_client = Client()

async def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

async def get_weather_gpt(city):
    try:
        prompt = f"Какова погода в городе {city} сейчас?"
        response = gpt_client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content if response.choices else None
    except Exception:
        return None

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("🎬 Привет! Это бот для отбора в фильм. Просто отправьте своё фото!\n"
                         "☁️ Также я могу показывать погоду! Используйте команду:\n"
                         "`/weather [город]` или просто напишите `погода [город]`.", 
                         parse_mode="Markdown")

@router.message(Command("weather"))
async def weather_command(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Пожалуйста, укажите город. Например: `/weather Tashkent`", parse_mode="Markdown")
        return

    city = args[1]
    data = await get_weather(city)
    
    if data and "main" in data:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].capitalize()
        await message.answer(f"🌤 Погода в городе {city}:\n🌡 Температура: {temp}°C\n☁️ {desc}")
    else:
        gpt_weather = await get_weather_gpt(city)
        if gpt_weather:
            await message.answer(f"🤖 По данным AI:\n{gpt_weather}")
        else:
            await message.answer("❌ Город не найден или произошла ошибка. Попробуйте еще раз!")
            await bot.send_message(ADMIN_ID, f"⚠️ Ошибка с погодой!\nГород: {city}\nПользователь: {message.from_user.full_name} ({message.from_user.id})")

@router.message(lambda message: message.text.lower().startswith("погода"))
async def weather_text(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Укажите город после слова `погода`. Например: `погода Ташкент`")
        return

    city = args[1]
    data = await get_weather(city)
    
    if data and "main" in data:
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].capitalize()
        await message.answer(f"🌤 Погода в городе {city}:\n🌡 Температура: {temp}°C\n☁️ {desc}")
    else:
        gpt_weather = await get_weather_gpt(city)
        if gpt_weather:
            await message.answer(f"🤖 По данным AI:\n{gpt_weather}")
        else:
            await message.answer("❌ Город не найден или произошла ошибка. Попробуйте еще раз!")
            await bot.send_message(ADMIN_ID, f"⚠️ Ошибка с погодой!\nГород: {city}\nПользователь: {message.from_user.full_name} ({message.from_user.id})")

@router.message(lambda message: message.text is not None)
async def handle_text(message: types.Message):
    user_info = f"📩 Новое сообщение!\n👤 {message.from_user.full_name}\n🆔 ID: {message.from_user.id}"
    if message.from_user.username:
        user_info += f"\n🔗 Username: @{message.from_user.username}"
    user_info += f"\n\n💬 Сообщение: {message.text}"

    await bot.send_message(ADMIN_ID, user_info)

@router.message(lambda message: message.photo is not None)
async def handle_photo(message: types.Message):
    photo = message.photo[-1].file_id
    caption = f"🖼 Новое фото!\n👤 Имя: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}"
    if message.from_user.username:
        caption += f"\n🔗 Username: @{message.from_user.username}"
    if message.caption:
        caption += f"\n✏️ Описание: {message.caption}"

    await bot.send_photo(ADMIN_ID, photo, caption=caption)

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

dp.include_router(router)

async def on_start():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(on_start())
