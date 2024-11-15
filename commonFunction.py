import json

from flask import session
from applogging import write_log
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
        userid = session.get('userid', None)
        cookie = session.get('cookie', None)
        if userid:
            body['USERID'] = userid
        if cookie:
            body['COOKIE'] = cookie

        max_retries = 3
        for attempt in range(max_retries):
            write_log(f"POST request to {url} with body {body} (attempt {attempt + 1}/{max_retries})")
            response = requests.post(url, headers=headers, data=json.dumps(body))
            write_log(f"POST request to {url} with body {body} returned status code {response.status_code}")
            if response.status_code != 503:
                return response.json()
            time.sleep(1)  # Wait for 1 second before retrying

        return f"Error making POST request: received status code 503 after {max_retries} retries"
    except requests.exceptions.RequestException as e:
        return f"Error making POST request: {str(e)}"

def check_logged_in_or_not():
    session_cookie = session.get('cookie', None)
    if session_cookie is None:
        return False
    return True