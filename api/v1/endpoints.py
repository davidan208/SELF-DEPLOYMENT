from fastapi import APIRouter
from services import service_openai, service_base, service_github

router = APIRouter()

@router.post(
    "/chat",
    description = "Chat with the bot"
)
async def chat(prompt: str):
    return service_base.chat(prompt)


@router.post(
    "/check",
    description = "Testing function"
)
async def check(check: bool = True):
    return await service_github.github_check()


@router.post(
    "/merge",
    description = "Merge two branch"
)
async def merge():
    return await service_github.github_merge()