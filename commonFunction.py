import git

def git_clone_repo(repo_url, target_directory):
    try:
        # Use GitPython to clone the repo
        git.Repo.clone_from(repo_url, target_directory)
        return True
    except git.GitError as e:
        return f"Error cloning repository: {str(e)}"