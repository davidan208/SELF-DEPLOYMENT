from typing import List, Any
from github import Github, Auth, GithubException
from configs.config import settings


def get_github_instance() -> Github:
    return Github(auth=Auth.Token(settings.GITHUB_TOKEN))


def get_deployment_repo(repo_name: str = "SELF-DEPLOYMENT") -> Any:
    github_instance = get_github_instance()
    user = github_instance.get_user()
    for repo in user.get_repos():
        if not repo.fork and repo.name == repo_name:
            return repo
    raise ValueError(f"Repository '{repo_name}' not found.")


def list_repo_structure(repo: Any, path: str = "") -> List[str]:
    file_paths: List[str] = []
    contents = repo.get_contents(path)
    for content in contents:
        if content.type == "dir":
            file_paths.extend(list_repo_structure(repo, content.path))
        else:
            file_paths.append(content.path)
    return file_paths


async def github_check() -> List[str]:
    repo = get_deployment_repo()
    return list_repo_structure(repo)


async def github_merge() -> Any:
    repo = get_deployment_repo()
    base_branch = "main"
    head_branch = "dev"
    commit_message = "Auto merge branch 'dev' into 'main'"
    try:
        merge_result = repo.merge(base=base_branch, head=head_branch, commit_message=commit_message)
        return merge_result
    except GithubException as e:
        return {"error": str(e)}


async def github_code_change(content: str) -> Any:
    repo = get_deployment_repo()
    branch = "dev"
    file_path = "updated_file.py"
    commit_message = f"Update {file_path}"
    try:
        file_content = repo.get_contents(file_path, ref=branch)
        update_result = repo.update_file(
            path=file_content.path,
            message=commit_message,
            content=content,
            sha=file_content.sha,
            branch=branch
        )
        return update_result
    except GithubException:
        create_result = repo.create_file(
            path=file_path,
            message=commit_message,
            content=content,
            branch=branch
        )
        return create_result