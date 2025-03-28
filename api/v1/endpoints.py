from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from services import service_base
from services.service_github import GitHubRepo
from .. import get_admin_access, get_access_token
from configs.config import superuser_auth



router = APIRouter()

@router.post(
    "/chat",
    tags = ["Chat với AI tuỳ chọn"],
)
async def chat(prompt: str, provider: str, model_name: str, history = []):
    return await service_base.chat_llm(
        user_query=prompt,
        provider = provider,
        model_name = model_name,
        history = history
    )

@router.post(
    "/get_structure",
    tags = ["Kiểm tra nội dung github"]
)
async def github_check(repo_name: str, access_token: str):
    github_login = GitHubRepo(access_token)
    return await github_login.get_structure(repo_name)


@router.post(
    "/fork",
    tags = ["Fork repo github"]
)
async def fork_github(access_token: str, repo_name):
    github_login = GitHubRepo(access_token)
    return await github_login.fork_repo(repo_name)


@router.post(
    "/understand_github",
    tags = ["Đọc hiểu nội dung repo"]
)
async def understand_github(access_token: str, repo_name):
    github_login = GitHubRepo(access_token)
    list_files = github_login.get_structure()


@router.post(
    "/repo_languages",
    tags = ["Tổng hợp thông tin cần biết về github"]
)
async def get_repo_languages(repo_name: str, access_token: str):
    github_login = GitHubRepo(access_token)
    return await github_login.get_language(repo_name)

@router.post(
    "/merge", 
    tags = ["Merge dev vào prod"]
)
async def merge_branch(repo_name: str, access_token: str ,admin_access_token = Depends(get_admin_access)):
    if admin_access_token != superuser_auth.SUPERUSER_TOKEN:
        return "YOU ARE NOT ALLOWED"
    
    github_login = GitHubRepo(access_token)
    if await github_login.merge_branch(
        repo_name = repo_name,
        head_branch = "dev",
        base_branch = await github_login.get_default_branch(repo_name)
    ):
        ...


    # if admin_access_token not in []
    # return admin_access_token


