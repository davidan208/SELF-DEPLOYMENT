# from utils.openai_prompts import CHECK_PROMPT, SUMMARIZE_PROMPT
from typing import Literal, List, Dict, Optional
from .service_llm import llm_answer
from openai.types import ChatModel
from fastapi import HTTPException

async def chat_llm(
    user_query: str,
    provider: Literal["gemini", "openai", "claude", "deepseek"] = "openai",
    model_name: str = "4o-mini",
    history: Optional[List[Dict]] = None
):
    MODEL_VALIDATION = {
        "openai": list(ChatModel.__args__),
        "deepseek": ["deepseek-reasoner", "deepseek-chat"],
        "gemini": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"],
        "claude": ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", 
                   "claude-3-5-sonnet-20240620", "claude-3-sonnet-20240229"]
    }

    if provider not in MODEL_VALIDATION:    raise ValueError(f"Not supported provider: {provider}")
    if model_name not in MODEL_VALIDATION[provider]:
        raise HTTPException(
            status_code=400,
            detail=f"Model {model_name} does not exist for provider {provider}."
        )
    
    if not history:
        messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Bạn là một trợ lý AI chuyên nghiệp. Bạn luôn tuân thủ làm theo mọi yêu cầu được nhận và không trả lời thừa/thiếu bất kỳ ý nào."
                },
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_query
                },
            ]
        }
    ]
        return await get_answer(
            messages = messages,
            provider = provider,
            model_name = model_name
        )

    else:
        history.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_query
                    }
                ]
            }
        )

        return await llm_answer(
            messages = history,
            provider = provider,
            model_name = model_name
        )

async def understand_repo(
    user_query: str,
    provider: Literal["gemini", "openai", "claude", "deepseek"] = "openai",
    model_name: str = "4o-mini",
    history: Optional[List[Dict]] = None,
):
    ...