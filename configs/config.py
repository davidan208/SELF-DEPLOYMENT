from pydantic.v1 import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
    OPENAI_TOKEN: str = os.getenv("OPENAI_TOKEN")
    CLAUDE_TOKEN: str = os.getenv("CLAUDE_TOKEN")
    DEEPSEEK_TOKEN: str = os.getenv("DEEPSEEK_TOKEN")
    GEMINI_TOKEN: str = os.getenv("GEMINI_TOKEN")

settings = Settings()

class SUPERUSER(BaseSettings):
    SUPERUSER_TOKEN: str = os.getenv("SUPER_USER_TOKEN")

superuser_auth = SUPERUSER()