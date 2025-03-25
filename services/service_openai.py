from openai import OpenAI
from configs.config import settings

def call_openai(messages: list = [], search: bool = False, model: str = "o4-mini"):
    client = OpenAI(client = settings.OPENAI_TOKEN)
    
    if search:
        openai_model = model + "-search-preview"

    response = client.chat.completions.create(
        model = openai_model,
        messages = messages
    )
    return response.choices[0].message["content"]


