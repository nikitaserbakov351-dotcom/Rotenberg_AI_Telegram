# Telegram-бот с интеграцией Google Gemini

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-API-8E75B2?logo=googlegemini&logoColor=white)
![Function Calling](https://img.shields.io/badge/Function%20Calling-weather%20API-4285F4)
![Tests](https://github.com/nikitaserbakov351-dotcom/Rotenberg_AI_Telegram/actions/workflows/tests.yml/badge.svg)

Асинхронный Telegram-бот на базе большой языковой модели Google Gemini. Проект демонстрирует полный цикл интеграции LLM в практический продукт: управление системным промптом, ведение диалогового контекста, вызов внешних API через механизм Function Calling и безопасную работу с ключами.

## Ключевые возможности

- **Ролевое моделирование** — модели задан системный промпт, формирующий характер, стиль речи и фоновые знания персонажа для органичного ведения диалога.
- **Управление контекстом** — бот хранит историю переписки в скользящем окне памяти: устаревшие реплики автоматически вытесняются, что удерживает расход токенов и нагрузку на API в заданных пределах.
- **Function Calling** — модель самостоятельно принимает решение обратиться к внешнему инструменту `get_weather`; бот выполняет запрос к OpenWeatherMap, парсит JSON-ответ и возвращает данные в LLM для формирования финального ответа (двухшаговый сценарий вызова).
- **Безопасность конфигурации** — все ключи передаются через переменные окружения (`.env`, в репозитории только шаблон `.env.example`); на старте проверяется наличие обязательных ключей.
- **Отказоустойчивость** — ошибки сетевых запросов и API обрабатываются и не приводят к падению бота; проксирование трафика включается опционально через конфигурацию.
- **Тестируемость** — логика выделена в чистые функции и покрыта pytest (скользящее окно контекста, конфигурация прокси, обработка отсутствующих ключей); CI на GitHub Actions.

## Технологический стек

| Компонент | Технология |
|---|---|
| Язык | Python 3.10+, asyncio |
| Telegram | Aiogram 3 (long polling) |
| LLM | Google Gemini API (`generateContent`) |
| HTTP | HTTPX (async-клиент) |
| Конфигурация | python-dotenv |

## Быстрый старт

```bash
git clone https://github.com/nikitaserbakov351-dotcom/Rotenberg_AI_Telegram.git
cd Rotenberg_AI_Telegram

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # заполните ключи доступа
python main.py
```

Для запуска тестов (сетевые вызовы не выполняются):

```bash
pip install -r requirements-dev.txt
pytest -v
```

В `.env` необходимо указать:

| Переменная | Назначение |
|---|---|
| `TELEGRAM_TOKEN` | токен бота от [@BotFather](https://t.me/BotFather) |
| `GEMINI_API_KEY` | ключ Google AI Studio |
| `WEATHER_API_KEY` | ключ OpenWeatherMap (для Function Calling) |
| `PROXY_URL` *(опционально)* | исходящий прокси, если сеть требует явный шлюз |

## Особенности реализации

**Двухшаговый Function Calling.** При получении `functionCall` от модели бот формирует `functionResponse` с реальными данными о погоде и повторно обращается к API — ответ генерируется на основе свежих внешних данных, а не знаний модели.

**Скользящее окно контекста.** История диалога хранится в памяти процесса парами «реплика–ответ»; при превышении лимита из начала очереди удаляются по две записи. Диалоги разных чатов изолированы друг от друга по `chat_id`.

**Человекоподобная подача.** Имитация «печатает…», пауза, пропорциональная длине ответа, и стилистика сообщений заданы на уровне промпта и логики отправки.

## Структура проекта

```
├── main.py                    # логика бота: промпт, работа с API, Function Calling
├── conftest.py                # фиктивные ключи для тестовой среды
├── test_bot.py                # pytest: окно контекста, конфигурация, ключи
├── .env.example               # шаблон конфигурации (сами ключи в репозиторий не попадают)
├── .github/workflows/tests.yml
└── requirements.txt           # зависимости (+ requirements-dev.txt для тестов)
```

## Развитие проекта

- [ ] Хранение контекста в Redis вместо памяти процесса
- [ ] Дополнительные инструменты: курсы валют, поиск, калькулятор
- [ ] Ограничение частоты запросов (anti-flood)
- [ ] Dockerfile и деплой на VPS

## Автор

Проект подготовлен **[@TheSheinAir](https://github.com/TheSheinAir)** — другие работы смотрите в [профиле GitHub](https://github.com/TheSheinAir?tab=repositories).
