import asyncio
import aiohttp
from github import Github, Auth
from github.GithubException import UnknownObjectException, GithubException

import re
from ghapi.all import GhApi


class GitHubRepo:
    def __init__(self, access_token):
        self.access_token = access_token
        self.github = self.login()
        self.user = self.github.get_user().login
        self.api  = GhApi(token = access_token)

    def login(self):
        auth = Auth.Token(self.access_token)
        return Github(auth=auth)

    def regex_handling(self, repo_name):
        pattern = r"github\.com/([^/]+/[^/.]+)"
        if re.search(pattern, repo_name):
            repo_name = re.search(pattern, repo_name).group(1)
            repo_name = repo_name.replace(".git", "")
        
        return repo_name

    async def get_repo(self, repo_name):
        """Async version of get_repo"""
        if "/" not in repo_name:
            repo_name = f"{self.user}/{repo_name}"
        
        repo_name = self.regex_handling(repo_name = repo_name)

        print(f"Trying to get repo: {repo_name}")
        try:
            return await asyncio.to_thread(self.github.get_repo, repo_name)
        except UnknownObjectException as e:
            print(f"Error finding repo {repo_name}: {str(e)}")
            return None

    async def get_branches(self, repo_name, default = False):
        repo = await self.get_repo(repo_name)
        if repo is None:
            return None
        
        if default: return await asyncio.to_thread(lambda: repo.default_branch)
        branches = await asyncio.to_thread(repo.get_branches)
        return [branch.name for branch in branches]
    
    async def get_structure(self, repo_name, branch = None):
        repo = await self.get_repo(repo_name = repo_name)
        if repo is None: 
            print(f"Repository {repo_name} not found")
            return None

        if branch is None: 
            branch = await asyncio.to_thread(lambda: repo.default_branch)
            print(f"Using default branch: {branch}")

        try:
            print(f"Getting branch {branch} for repo {repo_name}")
            branch_obj = await asyncio.to_thread(lambda: repo.get_branch(branch))
        except Exception as e: 
            print(f"Error getting branch {branch}: {str(e)}")
            return None

        commit_sha = branch_obj.commit.sha
        print(f"Getting tree for commit: {commit_sha}")

        try:
            tree = await asyncio.to_thread(lambda: repo.get_git_tree(commit_sha, recursive=True))
        except GithubException as e:
            print(f"Error getting git tree: {str(e)}")
            return None
        
        files = [item.path for item in tree.tree if item.type == 'blob']
        return files

    async def get_files_content(self, repo_name, branch = None, files: list[str] = [], forbidden_extensions=None):

        if not files: 
            print("No files provided")
            return None

        # Chuẩn hóa forbidden_extensions
        if forbidden_extensions:
            forbidden_extensions = [ext.lower() if not ext.startswith('.') else ext[1:].lower() 
                                 for ext in forbidden_extensions]

        repo = await self.get_repo(repo_name = repo_name)
        if repo is None: 
            print(f"Repository {repo_name} not found")
            return None

        if branch is None: 
            branch = await asyncio.to_thread(lambda: repo.default_branch)
            print(f"Using default branch: {branch}")

        try:
            # Kiểm tra branch tồn tại
            await asyncio.to_thread(lambda: repo.get_branch(branch))
        except Exception as e:
            print(f"Branch {branch} not found: {str(e)}")
            return None
        
        available_files = await self.get_structure(repo_name = repo_name, branch = branch)
        if available_files is None:
            print(f"Could not get structure for repository {repo_name} branch {branch}")
            return None

        file_contents = {}

        for file in files:
            # Kiểm tra file có tồn tại trong repo không
            if file not in available_files:
                print(f"File {file} not found in repository {repo_name}")
                file_contents[file] = None
                continue

            # Kiểm tra extension có bị cấm không
            if forbidden_extensions:
                file_ext = file.split('.')[-1].lower() if '.' in file else ''
                if file_ext in forbidden_extensions:
                    print(f"File {file} has forbidden extension {file_ext}")
                    file_contents[file] = None
                    continue

            try:
                content = await asyncio.to_thread(lambda: repo.get_contents(file, ref=branch))
                
                # Kiểm tra kích thước file
                if content.size > 1024 * 1024:  # Lớn hơn 1MB
                    print(f"File {file} is too large ({content.size} bytes)")
                    file_contents[file] = None
                    continue

                try:
                    file_contents[file] = content.decoded_content.decode("utf-8")
                    print(f"Successfully retrieved content for {file}")
                except UnicodeDecodeError:
                    print(f"File {file} is not a text file")
                    file_contents[file] = None
            except Exception as e:
                print(f"Error getting content for {file}: {str(e)}")
                file_contents[file] = None

        return file_contents

    async def get_langauges(self, repo_name):
        if "/" not in repo_name: repo_name = f"{self.user}/{repo_name}"

        repo = await self.get_repo(repo_name = repo_name)
        if repo is None: return None

        try:
            languages = await asyncio.to_thread(repo.get_languages)
            total_bytes = sum(languages.values())
            if total_bytes == 0: return {}
            return {
                lang: (bytes_count / total_bytes) * 100 for lang, bytes_count in languages.items()
            }
        except Exception as e:
            print(f"Error getting languages: {e}")
            return None

    async def get_commit_history(self, repo_name, branch=None, file_path=None):
        repo_name = self.regex_handling(repo_name = repo_name)
        
        try:
            # Xử lý repo_name để lấy owner và repo
            owner, repo = repo_name.split('/') if '/' in repo_name else (self.user, repo_name)
            
            # Xác định branch nếu không được cung cấp
            if branch is None:
                repo_obj = await self.get_repo(repo_name)
                if repo_obj is None:
                    print(f"Repository {repo_name} not found")
                    return None
                
                branch = await asyncio.to_thread(lambda: repo_obj.default_branch)
                print(f"Using default branch: {branch}")

            if file_path is None:
                # Lấy lịch sử commit của toàn bộ repo
                try:
                    commits = await asyncio.to_thread(
                        lambda: list(self.github.get_repo(repo_name).get_commits(sha=branch))
                    )
                    commit_history = {
                        commit.sha: commit.commit.message
                        for commit in commits
                    }
                    print(f"Retrieved {len(commit_history)} commits from repository")
                    return commit_history
                except Exception as e:
                    print(f"Error getting repository commit history: {str(e)}")
                    return None
            else:
                # Kiểm tra file có tồn tại không
                try:
                    file_content = self.api.repos.get_content(
                        owner=owner,
                        repo=repo,
                        path=file_path,
                        ref=branch
                    )
                    print(f"Found file: {file_path}")
                except Exception as e:
                    print(f"File {file_path} not found: {str(e)}")
                    return None
                    
                # Lấy lịch sử commit của file với phân trang
                try:
                    all_commits = []
                    page = 1
                    per_page = 100  # Số lượng commit tối đa cho mỗi trang
                    
                    while True:
                        commits = self.api.repos.list_commits(
                            owner=owner,
                            repo=repo,
                            sha=branch,
                            path=file_path,
                            per_page=per_page,
                            page=page
                        )
                        
                        if not commits:  # Không còn commit nào nữa
                            break
                            
                        all_commits.extend(commits)
                        print(f"Retrieved {len(commits)} commits from page {page}")
                        
                        if len(commits) < per_page:  # Đã lấy hết tất cả commit
                            break
                            
                        page += 1
                    
                    commit_history = {
                        commit['sha']: commit['commit']['message']
                        for commit in all_commits
                    }
                    
                    print(f"Total commits retrieved for file: {len(commit_history)}")
                    return commit_history
                    
                except Exception as e:
                    print(f"Error getting commit history for file {file_path}: {str(e)}")
                    return None

        except Exception as e:
            print(f"Error in get_commit_history: {str(e)}")
            return None

    async def get_commit_changes(
        self, 
        repo_name, 
        branch=None, 
        file_path=None, 
        commit_id=None
    ):
        repo_name = self.regex_handling(repo_name=repo_name)
        
        try:
            owner, repo = repo_name.split('/') if '/' in repo_name else (self.user, repo_name)
            
            # Xác định branch mặc định
            if branch is None:
                repo_obj = await self.get_repo(repo_name)
                if not repo_obj:
                    print(f"Repository {repo_name} not found")
                    return None
                branch = repo_obj.default_branch
                print(f"Using default branch: {branch}")

            # Lấy lịch sử commit
            commit_history = await self.get_commit_history(
                repo_name=repo_name,
                branch=branch,
                file_path=file_path
            )
            
            if not commit_history:
                print("No commit history found")
                return None

            # Xác định commit mục tiêu
            target_commit = commit_id if commit_id else next(iter(commit_history))
            if target_commit not in commit_history:
                print(f"Commit {target_commit} not found")
                return None

            # Lấy thông tin commit
            try:
                commit = await asyncio.to_thread(
                    lambda: self.api.repos.get_commit(
                        owner=owner,
                        repo=repo,
                        ref=target_commit
                    )
                )
            except Exception as e:
                print(f"Error getting commit: {str(e)}")
                return None

            # Chuẩn hóa đường dẫn thư mục
            normalized_path = file_path.rstrip('/') + '/' if file_path else ''
            
            # Xử lý từng file trong commit
            result = {
                "commit_id": target_commit,
                "message": commit.commit.message,
                "date": commit.commit.author.date,
                "author": {
                    "name": commit.commit.author.name,
                    "email": commit.commit.author.email
                },
                "files": {}
            }

            for file in commit.files:
                try:
                    # Kiểm tra file thuộc thư mục đích (nếu có)
                    if file_path:
                        if not file.filename.startswith(normalized_path):
                            continue

                    # Lấy nội dung file tại commit này
                    content = ""
                    if file.status != "removed":
                        try:
                            content_res = await asyncio.to_thread(
                                lambda: self.api.repos.get_content(
                                    owner=owner,
                                    repo=repo,
                                    path=file.filename,
                                    ref=target_commit
                                )
                            )
                            content = self._decode_content(content_res.content)
                        except Exception as e:
                            print(f"Error getting content for {file.filename}: {str(e)}")

                    # Thêm thông tin thay đổi
                    result["files"][file.filename] = {
                        "status": file.status,
                        "changes": file.changes,
                        "additions": file.additions,
                        "deletions": file.deletions,
                        "content": content,
                        "patch": getattr(file, "patch", None)
                    }

                except Exception as e:
                    print(f"Error processing {file.filename}: {str(e)}")

            return result if result["files"] else None

        except Exception as e:
            print(f"Critical error: {str(e)}")
            return None