from fastapi import APIRouter, Depends, HTTPException
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
    "/branch",
    tags = ["Lấy thông tin các branch"]
)
async def get_branch(repo_name: str, access_token: str = Depends(get_access_token), default: bool = False):
    gh = GitHubRepo(access_token = access_token)
    branches = await gh.get_branches(repo_name = repo_name, default = default)
    if branches is None:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return branches

@router.post(
    "/structure",
    tags = ["Lấy cấu trúc dạng cây của một repo"]
)
async def get_structure(repo_name: str, branch: str = None, access_token: str = Depends(get_access_token)):
    gh = GitHubRepo(access_token = access_token)
    repo_structure = await gh.get_structure(repo_name = repo_name, branch = branch)
    if repo_structure is None:
        raise HTTPException(status_code=404, detail="Repository or branch is not found")

    return repo_structure

@router.post(
    "/get_content",
    tags = ["Lấy nội dung các file"]
)
async def get_content(
    repo_name: str, 
    branch: str, 
    access_token: str = Depends(get_access_token), 
    files: list[str] = None,
    forbidden_extensions: list[str] = None
):
    gh = GitHubRepo(access_token = access_token)
    contents = await gh.get_files_content(
        repo_name = repo_name, 
        branch = branch, 
        files = files,
        forbidden_extensions = forbidden_extensions
    )
    if not contents:
        raise HTTPException(status_code=404, detail="Repo / branch / files not found")
    
    return contents

@router.post(
    "/get_commit_history",
    tags = ["Lấy lịch sử commit của một repository hoặc một file cụ thể"]
)
async def get_commit_history(repo_name: str, branch: str = None, file_path: str = None, access_token: str = Depends(get_access_token)):
    gh = GitHubRepo(access_token = access_token)
    commit_history = await gh.get_commit_history(repo_name = repo_name, branch = branch, file_path = file_path)
    if commit_history is None:
        raise HTTPException(status_code=404, detail="Repository or branch or file not found")
    return commit_history

@router.post(
    "/get_changes",
    tags = ["Tổng hợp nội dung thay đổi qua các commit"]
)
async def get_commit_changes(
    repo_name: str, 
    branch: str = None, 
    file_path: str = None, 
    commit_id: str = None,
    access_token: str = Depends(get_access_token)
):
    """
    Lấy nội dung thay đổi của một repository, thư mục, hoặc file cụ thể
    
    - **repo_name**: Tên repository
    - **branch**: Tên branch (nếu không cung cấp sẽ dùng branch mặc định)
    - **file_path**: Đường dẫn đến file hoặc thư mục cần xem thay đổi
    - **output_diff**: Có hiển thị diff chi tiết hay không
    - **include_file_content**: Có bao gồm nội dung file trước và sau khi thay đổi hay không
    - **start_id**: Commit mới nhất (nếu không cung cấp sẽ dùng commit mới nhất trong lịch sử)
    - **end_id**: Commit cũ nhất (nếu không cung cấp sẽ dùng commit cũ nhất trong lịch sử)
    """
    gh = GitHubRepo(access_token = access_token)
    changes = await gh.get_commit_changes(
        repo_name = repo_name,
        branch = branch,
        file_path = file_path,
        commit_id = commit_id
    )
    
    if changes is None:
        raise HTTPException(
            status_code=404, 
            detail="Repository, branch, commit hoặc file không tìm thấy"
        )
    
    return changes