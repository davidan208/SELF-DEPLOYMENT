import asyncio
import aiohttp
from github import Github, Auth
from github.GithubException import UnknownObjectException, GithubException

class GitHubRepo:
    def __init__(self, access_token):
        self.access_token = access_token
        self.github = self.login()
        self.user = self.github.get_user().login

    def login(self):
        auth = Auth.Token(self.access_token)
        return Github(auth=auth)

    async def get_repo(self, repo_name):
        """Async version of get_repo"""
        if "/" not in repo_name:
            repo_name = f"{self.user}/{repo_name}"
        
        try:
            return await asyncio.to_thread(self.github.get_repo, repo_name)
        except UnknownObjectException:
            return None

    async def fetch_files(self, repo, path=""):
        """Async generator for files"""
        try:
            contents = repo.get_contents(path)
            for content in contents:
                if content.type == "dir":
                    async for file_path in self.fetch_files(repo, content.path):
                        yield file_path
                else:
                    yield content.path
        except Exception as e:
            print(f"Error fetching contents: {e}")

    async def get_structure(self, repo_name):
        repo = await self.get_repo(repo_name)
        if not repo:
            return []
        return [path async for path in self.fetch_files(repo)]
    
    async def get_content(self, repo_name, path):
        repo = await self.get_repo(repo_name=repo_name)
        if not repo: 
            return "Repo not exist"
        try:
            file_content = repo.get_contents(path)
            return file_content.decoded_content.decode("utf-8")
        except Exception as e:
            return f"Error fetching this file: {repo_name}/{path}"
        
    async def fork_repo(self, repo_name):
        if "/" not in repo_name:
            print("Invalid repository format. Use 'owner/repo'.")
            return None
        
        _, repo = repo_name.split("/")
        new_repo_name = f"{self.user}/{repo}"

        # Check if the forked repo already exists
        if await self.get_repo(new_repo_name):
            print(f"Fork already exists: {new_repo_name}")
            return None
        
        repo = await self.get_repo(repo_name)
        if not repo:
            print("Repository not found.")
            return None
        
        try:
            forked_repo = repo.create_fork()
            print(f"Repository forked successfully: {forked_repo.full_name}")
            return forked_repo.full_name
        except Exception as e:
            print(f"Error forking repository: {e}")
            return None
        
    async def get_language(self, repo_name):
        if "/" not in repo_name:
            repo_name = f"{self.user}/{repo_name}"

        repo = await self.get_repo(repo_name)
        if not repo:
            return None
        
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
        
    async def write_code(
        self,
        repo_name: str,
        branch: str = "dev",
        files: dict = {},
        commit_message: str = "",
    ):
        
        try:
            repo = await self.get_repo(repo_name)
            if not repo:    return False

            try:
                ref = await asyncio.to_thread(repo.get_git_ref, f"heads/{branch}")
                base_sha = repo.get_branch(branch).commit.sha
            except UnknownObjectException:
                if branch != "dev": return False
                default_branch = await asyncio.to_thread(lambda: repo.default_branch)
                base_sha = repo.get_branch(default_branch).commit.sha
                ref = await asyncio.to_thread(repo.create_git_ref, f"refs/heads/{branch}", base_sha)

            blobs = {}
            for path, content in files.items():
                blob = await asyncio.to_thread(repo.create_git_blob, content, "utf-8")
                blobs[path] = blob.sha

            commit = await asyncio.to_thread(repo.get_git_commit, base_sha)
            tree = await asyncio.to_thread(
                repo.create_git_tree,
                [{
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": sha
                } for path, sha in blobs.items()],
                base_tree=commit.tree
            )

            new_commit = await asyncio.to_thread(
                repo.create_git_commit,
                commit_message,
                tree.sha,
                [commit.sha]
            )

            # Update branch
            await asyncio.to_thread(ref.edit, new_commit.sha)
            return True

        except Exception as e:
            print(f"Error writing code: {str(e)}")
            return False

    async def get_default_branch(self, repo_name: str):
        repo = await self.get_repo(repo_name = repo_name)
        return repo.default_branch if repo else None
     
    async def merge_branch(
        self,
        repo_name: str,
        head_branch: str,     # mostly dev
        base_branch: str,     # mostly main/master - default branch
        commit_message: str = "Merge branches via API"
    ) -> bool:
        try:
            repo = await self.get_repo(repo_name)
            if not repo:    return False

            if not base_branch: base_branch = await self.get_default_branch(repo_name)

            head_ref = await asyncio.to_thread(repo.get_git_ref, f"heads/{head_branch}")
            base_ref = await asyncio.to_thread(repo.get_git_ref, f"heads/{base_branch}")

            merge_result = await asyncio.to_thread(
                repo.merge,
                base_ref.ref,
                head_ref.object.sha,
                commit_message
            )

            return merge_result is not None
        
        except GithubException as e:
            print(f"Reset failed: {e.data.get('message', 'Unknown error')}")
            return False
        except Exception as e:
            print(f"Error resetting branch: {str(e)}")
            return False
        
    async def revert_to_commit(
        self,
        repo_name: str,
        commit_sha: str,
        branch: str = None
    ) -> bool:
        """
        Revert to a specific commit in the repository's history
        :param commit_sha: The commit SHA to revert to
        :param branch: Target branch to update (defaults to default branch)
        """
        try:
            repo = await self.get_repo(repo_name)
            if not repo:
                return False

            if not branch:
                branch = await self.get_default_branch(repo_name)

            # GitHub API endpoint for reverting commits
            url = f"https://api.github.com/repos/{repo_name}/commits/{commit_sha}/revert"
            headers = {
                "Authorization": f"token {self.access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"branch": branch}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 201:
                        print(f"Reverted to commit {commit_sha} on branch {branch}")
                        return True
                    
                    error = await response.json()
                    print(f"Revert failed: {error.get('message', 'Unknown error')}")
                    return False

        except Exception as e:
            print(f"Error reverting commit: {str(e)}")
            return False
        
    async def get_commit_list(self, repo_name: str, branch: str = None, limit: int = 30) -> list:
        try:
            repo = await self.get_repo(repo_name)
            if not repo:
                return []

            if not branch:
                branch = await self.get_default_branch(repo_name)

            commits = []
            async for commit in await asyncio.to_thread(
                lambda: repo.get_commits(sha=branch)[:limit]
            ):
                commits.append({
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.author.login if commit.author else "Unknown",
                    "date": commit.commit.author.date
                })

            return commits

        except Exception as e:
            print(f"Error getting commits: {str(e)}")
            return []
        
    async def navigate_commits(self, repo_name: str, steps: int = 1, branch: str = None) -> bool:
        """
        Move branch pointer backward/forward in commit history
        :param steps: Positive numbers go forward, negative go backward
        """
        try:
            commits = await self.get_commit_list(repo_name, branch)
            if not commits:
                return False

            current_index = 0  # Latest commit is always index 0
            target_index = current_index + steps

            if target_index < 0 or target_index >= len(commits):
                print(f"Invalid step count: {steps}")
                return False

            return await self.reset_branch(
                repo_name,
                branch or await self.get_default_branch(repo_name),
                commits[target_index]["sha"]
            )

        except Exception as e:
            print(f"Navigation error: {str(e)}")
            return False
        
    async def reset_branch(self, repo_name: str, branch: str, commit_sha: str) -> bool:
        """
        Force reset a branch to a specific commit
        WARNING: This is a destructive operation!
        """
        try:
            repo = await self.get_repo(repo_name)
            if not repo:
                return False

            ref = await asyncio.to_thread(repo.get_git_ref, f"heads/{branch}")
            await asyncio.to_thread(ref.edit, commit_sha)
            print(f"Reset {branch} to commit {commit_sha}")
            return True

        except GithubException as e:
            print(f"Reset failed: {e.data.get('message', 'Unknown error')}")
            return False
        except Exception as e:
            print(f"Error resetting branch: {str(e)}")
            return False