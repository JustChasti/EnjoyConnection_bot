import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


token=os.getenv("BOT_TOKEN", "")
host=os.getenv("SERVER_HOST", "http://127.0.0.1:8080")
api_path=os.getenv("API_PATH", "/api/v1")
debug_mode=os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")

BASE_URL = f"{host}{api_path}"

PLAN_LABELS = {
    "month":   "1 месяц",
    "3months": "3 месяца",
    "year":    "1 год",
}

GENDER_LABELS = {"male": "Мужской", "female": "Женский"}
GOAL_LABELS = {"best_friend": "Лучшие друзья", "romantic": "Романтические партнёры"}
RELATIONSHIP_STAGE_LABELS = {
    "acquaintance": "Знакомство",
    "friend": "Дружба",
    "best_friend": "Лучшие друзья",
    "romantic": "Романтика",
}
# Путь стадий в зависимости от цели общения (для шкалы прогресса)
RELATIONSHIP_PATHS = {
    "best_friend": ["acquaintance", "friend", "best_friend"],
    "romantic":    ["acquaintance", "friend", "romantic"],
}
