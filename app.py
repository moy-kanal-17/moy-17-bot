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

@router.message()
async def handle_message(message: types.Message):
    user_text = message.text.lower()
    city = user_text.replace("погода", "").strip()

    if city:
        data = await get_weather(city)

        if data and "main" in data:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"].capitalize()
            reply_text = f"🌤 Погода в городе {city}:\n🌡 Температура: {temp}°C\n☁️ {desc}"
        else:
            gpt_weather = await get_weather_gpt(city)
            if gpt_weather:
                reply_text = f"🤖 По данным AI:\n{gpt_weather}"
            else:
                reply_text = "❌ Город не найден или произошла ошибка. Попробуйте еще раз!"
                await bot.send_message(ADMIN_ID, f"⚠️ Ошибка с погодой!\nГород: {city}\nПользователь: {message.from_user.full_name} ({message.from_user.id})")
    else:
        reply_text = "🔹 Вы можете узнать погоду, написав `погода [город]`."

    await message.answer(reply_text)
    await bot.send_message(ADMIN_ID, f"📩 Новое сообщение!\n👤 {message.from_user.full_name}\n🆔 {message.from_user.id}\n💬 {message.text}")

dp.include_router(router)

async def on_start():
    print("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(on_start())
