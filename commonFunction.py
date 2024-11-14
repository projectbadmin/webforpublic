import json
import git
import requests
import time

def git_clone_repo(repo_url, target_directory):
    try:
        # Use GitPython to clone the repo
        git.Repo.clone_from(repo_url, target_directory)
        return True
    except git.GitError as e:
        return f"Error cloning repository: {str(e)}"

def send_post_request(url, body):
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        max_retries = 3
        retries = 0
        while retries < max_retries:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error making POST request: {str(e)}"
