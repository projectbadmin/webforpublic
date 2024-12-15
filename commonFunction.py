import json
from flask import session
from applogging import write_log
import git
import requests

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


def findStreamRequestFromSession(requestid):
    for i in range(len(session['StreamRequest'])):
        if session['StreamRequest'][i]['ID'] == requestid:
            return session['StreamRequest'][i]
    return None


def findRequestFromSession(requestid, tempPageRequestID):
    for i in range(len(session['CloudBatchJobSubmitted'])):
        if session['CloudBatchJobSubmitted'][i]['ID'] == requestid:
            for j in range(len(session['CloudBatchJobSubmitted'][i]['CLOUDBATCHJOBLIST'])):
                if session['CloudBatchJobSubmitted'][i]['CLOUDBATCHJOBLIST'][j]['ID'] == tempPageRequestID:
                    return session['CloudBatchJobSubmitted'][i]['CLOUDBATCHJOBLIST'][j]
    
    for i in range(len(session['CloudBatchJobLocalDraft'])):
        if session['CloudBatchJobLocalDraft'][i]['ID'] == requestid:
            for j in range(len(session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'])):
                if session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'][j]['ID'] == tempPageRequestID:
                    return session['CloudBatchJobLocalDraft'][i]['CLOUDBATCHJOBLIST'][j]
    
    return None
    
    
    