"""Тесты конфигурации и утилит бота (без сетевых вызовов)."""
import asyncio

import main


def test_trim_history_trims_oldest_pairs():
    history = [{"role": r, "parts": [{"text": str(i)}]} for i, r in enumerate(["user", "model"] * 6)]
    main.trim_history(history)
    assert len(history) == 10
    assert history[0]["parts"][0]["text"] == "2"   # две самые старые реплики удалены
    assert history[-1]["parts"][0]["text"] == "11"


def test_trim_history_noop_within_limit():
    history = [{"role": "user", "parts": [{"text": "hi"}]}]
    main.trim_history(history)
    assert len(history) == 1


def test_trim_history_empty():
    history = []
    main.trim_history(history)
    assert history == []


def test_proxy_disabled_by_default():
    # в тестовой среде PROXY_URL не задан — бот работает напрямую
    assert main.PROXY_URL is None


def test_weather_without_key():
    # WEATHER_API_KEY в тестовой среде отсутствует — без сетевого вызова
    result = asyncio.run(main.get_weather("Москва"))
    assert "Ключ" in result
