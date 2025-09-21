# File: tools/tool_registry.py
from langchain.tools import tool
from github import Github, GithubException, UnknownObjectException
import os

def _get_github_instance():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ConnectionError("GITHUB_TOKEN not found in environment variables.")
    return Github(token)

@tool
def create_github_repo(repo_name: str, description: str = "", private: bool = False) -> str:
    """Creates a new GitHub repository."""
    try:
        g = _get_github_instance()
        user = g.get_user()
        repo = user.create_repo(name=repo_name, description=description, private=private)
        return f"SUCCESS: Repository '{repo.full_name}' created at {repo.html_url}"
    except GithubException as e:
        if e.status == 422:
            return f"ERROR: Repository '{repo_name}' likely already exists."
        return f"ERROR: Failed to create repository. Details: {e.data}"
    except Exception as e:
        return f"ERROR: An unexpected error occurred: {str(e)}"

@tool
def create_or_update_github_file(repo_name: str, file_path: str, content: str, commit_message: str) -> str:
    """Creates or updates a file in a specified GitHub repository."""
    try:
        g = _get_github_instance()
        user = g.get_user()
        repo_full_name = f"{user.login}/{repo_name}"
        repo = g.get_repo(repo_full_name)
        
        try:
            existing_file = repo.get_contents(file_path, ref="main")
            repo.update_file(path=existing_file.path, message=commit_message, content=content, sha=existing_file.sha, branch="main")
            return f"SUCCESS: File '{file_path}' was updated in repository '{repo_name}'."
        except UnknownObjectException:
            repo.create_file(path=file_path, message=commit_message, content=content, branch="main")
            return f"SUCCESS: File '{file_path}' was created in repository '{repo_name}'."
    except Exception as e:
        return f"ERROR: An unexpected error occurred: {str(e)}"

def get_all_tools():
    """Returns a list of all available tools."""
    return [
        create_github_repo,
        create_or_update_github_file,
    ]
