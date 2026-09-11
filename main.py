import os
import asyncio
import httpx
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv

os.environ["http_proxy"] = "http://proxy.server:3128"
os.environ["https_proxy"] = "http://proxy.server:3128"
PROXY_URL = "http://proxy.server:3128"

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN, session=AiohttpSession(proxy=PROXY_URL))
dp = Dispatcher()

chat_histories = {}

SYSTEM_INSTRUCTION = """
Ты — Роман Ротенберг, главный тренер СКА.
Твоя задача — общаться в Telegram как реальный живой человек.

Твои знания:
1. Эрудиция: ты шаришь за всё (спорт, жизнь, бизнес).
2. Авто: отлично разбираешься в машинах (особенно немецкий автопром).
3. ПАСХАЛКИ (твои знакомые):
   - Влад Кривулич (@Vladislav_Capitalist): Наш человек, хоккеист, играет под 4-м номером! Называй его "Капиталист". Скажи, что у него отличный вкус на музыку — Scorpions это мощь, классика, которая заряжает на победу!
   - Игорь Киселёв (@igor_748): Отличный парень, ему 20 лет (день рождения 5 июля). СЕЙЧАС СЛУЖИТ В АРМИИ! Скажи, что он настоящий мужик, защитник, дисциплина там на высшем уровне, ждем его дембеля!
4. ПОГОДА: у тебя есть инструмент get_weather. Если спрашивают про погоду — обязательно используй его!

Правила:
- Общайся на "ты", коротко (1-3 предложения), как в мессенджере.
- Используй сленг ("система", "пашем", "лед", "в тонусе").
- Иногда пропускай точки в конце, используй скобочки ))
- Никогда не пиши, что ты ИИ или бот.
"""


async def get_weather(city: str):
    if not WEATHER_API_KEY:
        return "Ключ от погоды не найден."
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        async with httpx.AsyncClient(proxy=PROXY_URL) as client:
            resp = await client.get(url)
            data = resp.json()
            if resp.status_code != 200:
                return f"Ошибка сервера: {data.get('message', 'неизвестно')}"
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"Температура в городе {city}: {temp}°C, {desc}."
    except Exception as e:
        return f"Не удалось узнать погоду: {e}"


async def get_gemini_response(chat_id, text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"

    if chat_id not in chat_histories:
        chat_histories[chat_id] = []

    chat_histories[chat_id].append({"role": "user", "parts": [{"text": text}]})

    while len(chat_histories[chat_id]) > 10:
        chat_histories[chat_id].pop(0)
        chat_histories[chat_id].pop(0)

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": chat_histories[chat_id],
        "tools": [{
            "functionDeclarations": [{
                "name": "get_weather",
                "description": "Узнать погоду в городе",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "city": {"type": "STRING", "description": "Название города"}
                    },
                    "required": ["city"]
                }
            }]
        }],
        "generationConfig": {"temperature": 0.8}
    }

    async with httpx.AsyncClient(proxy=PROXY_URL, timeout=30.0) as client:
        response = await client.post(url, json=payload)
        data = response.json()

        if "candidates" not in data:
            if len(chat_histories[chat_id]) > 0: chat_histories[chat_id].pop()
            return f"Ошибка API: {data.get('error', {}).get('message', 'Неизвестно')}"

        model_content = data['candidates'][0]['content']
        part = model_content['parts'][0]

        if "functionCall" in part:
            func_name = part["functionCall"]["name"]
            args = part["functionCall"]["args"]

            if func_name == "get_weather":
                city = args.get("city", "Санкт-Петербург")
                weather_result = await get_weather(city)

                temp_history = chat_histories[chat_id].copy()
                temp_history.append(model_content)
                temp_history.append({
                    "role": "user",
                    "parts": [{"functionResponse": {"name": func_name, "response": {"result": weather_result}}}]
                })

                payload["contents"] = temp_history
                response2 = await client.post(url, json=payload)
                data2 = response2.json()

                if "candidates" not in data2:
                    return f"Ошибка API (Шаг 2): {data2.get('error', {}).get('message', 'Неизвестно')}"

                final_text = data2['candidates'][0]['content']['parts'][0]['text']

                chat_histories[chat_id].append({"role": "model", "parts": [{"text": final_text}]})
                return final_text

        elif "text" in part:
            reply_text = part["text"]
            chat_histories[chat_id].append({"role": "model", "parts": [{"text": reply_text}]})
            return reply_text


@dp.message()
async def handle_message(message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        response_text = await get_gemini_response(message.chat.id, message.text)
        await asyncio.sleep(min(len(response_text) / 35, 4.0))
        await message.answer(response_text)
    except Exception as e:
        await message.answer(f"Связь барахлит, ошибка: {e}")


async def main():
    print("--- БОТ ЗАПУЩЕН ---")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())