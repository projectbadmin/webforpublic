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

        response = requests.post(url, headers=headers, data=json.dumps(body))
        write_log(f"POST request to {url} with body {body} returned status code {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error making POST request: {str(e)}"

def check_logged_in_or_not():
    session_userid = session.get('userid', None)
    session_cookie = session.get('cookie', None)
    if session_userid is None or session_cookie is None:
        return False
    else:
        response = send_post_request(
            'https://3iyu8yshel.execute-api.ap-south-1.amazonaws.com/check_valid_login', {}
        )
        message = response.get('message', 'No message found')
        if message == "Login session valid":
            return True
    return False