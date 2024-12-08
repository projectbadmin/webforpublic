import json
import os
import re
import shutil
import subprocess
import uuid

from flask import render_template, session

def fetch_result(application, cloudbatchjob_id):
    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = application.config['AWS_ACCESS_KEY_ID']
    env['AWS_SECRET_ACCESS_KEY'] = application.config['AWS_SECRET_ACCESS_KEY']
    tempResultFilePath = f"{application.config['temp_download_of_cloudBatchJobProgram_for_view_result']}{cloudbatchjob_id}.log"
    subprocess.run([f"aws s3 cp s3://projectbcloudbatchjoboutputfile/{cloudbatchjob_id}/{cloudbatchjob_id}.log {tempResultFilePath}"], capture_output=True, text=True, shell=True, env=env) 
    
    with open(tempResultFilePath, 'r') as file:
        result_content = file.read()
    
    os.remove(tempResultFilePath)
    
    return result_content