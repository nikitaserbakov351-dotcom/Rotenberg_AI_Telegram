"""Фиктивные ключи до импорта main: приложение не должно завершаться
sys.exit-ом в тестовой среде; прокси и ключ погоды гарантированно сброшены."""
import os

os.environ.setdefault("TELEGRAM_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.pop("PROXY_URL", None)
os.environ.pop("WEATHER_API_KEY", None)
