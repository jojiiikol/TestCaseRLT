import os

from dotenv import load_dotenv

load_dotenv()

class LLMConfig:
    api_key = os.getenv('LLM_API_KEY')

class DatabaseConfig:
    host = os.getenv('POSTGRES_HOST')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    database = os.getenv('POSTGRES_DB')

class BotConfig:
    bot_token = os.getenv('BOT_TOKEN')