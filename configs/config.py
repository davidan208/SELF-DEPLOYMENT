from pydantic.v1 import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

settings = Settings()


