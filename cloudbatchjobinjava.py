import json
import os
import re
import shutil
import subprocess
import uuid

from flask import render_template, session

commonJavaKeyWords = [
#    "System", "out", "println", "String", "Integer", "Double", "Boolean", "ArrayList", "HashMap", "HashSet", "List", "Map", "Set",
#    "public", "private", "protected", "static", "final", "void", "int", "double", "float", "char", "boolean", "long", "short", "byte",
#    "new", "return", "this", "super", "class", "interface", "extends", "implements", "package", "import", "try", "catch", "finally",
#    "throw", "throws", "synchronized", "volatile", "transient", "abstract", "enum", "instanceof", "assert", "break", "case", "continue",
#    "default", "do", "else", "for", "if", "goto", "switch", "while", "native", "strictfp"
]
classMethodsforOnStart = {}
classMethodsforOnProcess = {}
classMethodsforOnEnd = {}

def cloudbatchjobinjava(application, requestid, requestContentInJSON):
    read_javap_result(application)
    tempPageRequestID = str(uuid.uuid4())
    session[tempPageRequestID] = {
        'requestid': requestid,
        'requestContentInJSON': requestContentInJSON
    }
    shutil.rmtree(f"{application.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)
    return render_template('cloudbatchjobinjava.html', newReq=True, tempPageRequestID=tempPageRequestID, code_for_onStart="", code_for_onProcess="", code_for_onEnd="", alias="")


def cloudbatchjobinjava_edit_program_file(application, requestid, requestContentInJSON, cloudbatchjob_id, alias):
    read_javap_result(application)
    tempPageRequestID = cloudbatchjob_id
    cloudbatchjob_in_draft = False 
    for key in session.get('CloudBatchJobLocalDraft'):
        if key['ID'] == cloudbatchjob_id:
            cloudbatchjob_in_draft = True
            break
    
    if not cloudbatchjob_in_draft:
        session[tempPageRequestID] = {
            'requestid': requestid,
            'requestContentInJSON': requestContentInJSON
        }

    shutil.rmtree(f"{application.config['clone_of_cloudBatchJobTemplate']}{requestid}_interfaceOnly", ignore_errors=True)

    # use session value dirrectly
    if cloudbatchjob_in_draft:
        code_for_onStart = session.get(tempPageRequestID)['code_for_onStart']
        code_for_onProcess = session.get(tempPageRequestID)['code_for_onProcess']
        code_for_onEnd = session.get(tempPageRequestID)['code_for_onEnd']
        return render_template('cloudbatchjobinjava.html', newReq=False, tempPageRequestID=tempPageRequestID, code_for_onStart=code_for_onStart, code_for_onProcess=code_for_onProcess, code_for_onEnd=code_for_onEnd, alias=alias)


    # get the code for onStart, onProcess, onEnd
    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = application.config['AWS_ACCESS_KEY_ID']
    env['AWS_SECRET_ACCESS_KEY'] = application.config['AWS_SECRET_ACCESS_KEY']
    tempProgramFilePath = ""
    if(requestContentInJSON['FUT_OPT']=="F"):
        tempProgramFilePath = f"{application.config['temp_download_of_cloudBatchJobProgram_for_edit']}{cloudbatchjob_id}.java"
        subprocess.run([f"aws s3 cp s3://projectbcloudbatchjobprogramfile/{requestid}/{cloudbatchjob_id}/ForFutureData.java {tempProgramFilePath}"], capture_output=True, text=True, shell=True, env=env) 
    else:
        tempProgramFilePath = f"{application.config['temp_download_of_cloudBatchJobProgram_for_edit']}{cloudbatchjob_id}.java"
        subprocess.run([f"aws s3 cp s3://projectbcloudbatchjobprogramfile/{requestid}/{cloudbatchjob_id}/ForFutureData.java {tempProgramFilePath}"], capture_output=True, text=True, shell=True, env=env) 
    
    code_for_onStart = []
    code_for_onProcess = []
    code_for_onEnd = []
    with open(f"{tempProgramFilePath}", 'r') as file:
        lines = file.readlines()
        inside_method = None
        for line in lines:
            if f"onStart method start here - seceret - {application.config['SECRET_KEY']}" in line:
                inside_method = 'onStart'
            elif f"onProcess method start here - seceret - {application.config['SECRET_KEY']}" in line:
                inside_method = 'onProcess'
            elif f"onEnd method start here - seceret - {application.config['SECRET_KEY']}" in line:
                inside_method = 'onEnd'
            elif inside_method == 'onStart' and f"onStart method end here - seceret - {application.config['SECRET_KEY']}" in line:
                inside_method = None
            elif inside_method == 'onProcess' and f"onProcess method end here - seceret - {application.config['SECRET_KEY']}" in line:
                inside_method = None
            elif inside_method == 'onEnd' and f"onEnd method end here - seceret - {application.config['SECRET_KEY']}" in line:
                inside_method = None
            elif inside_method:
                if inside_method == 'onStart':
                    code_for_onStart.append(line.strip())
                elif inside_method == 'onProcess':
                    code_for_onProcess.append(line.strip())
                elif inside_method == 'onEnd':
                    code_for_onEnd.append(line.strip())

    code_for_onStart = '\n'.join(code_for_onStart)
    code_for_onProcess = '\n'.join(code_for_onProcess)
    code_for_onEnd = '\n'.join(code_for_onEnd)

    os.remove(tempProgramFilePath)

    return render_template('cloudbatchjobinjava.html', newReq=False, tempPageRequestID=tempPageRequestID, code_for_onStart=code_for_onStart, code_for_onProcess=code_for_onProcess, code_for_onEnd=code_for_onEnd, alias=alias)


def check_and_generate_keywords_(line, cursor_pos, method):
    match = re.search(r'(\w+)\.$', line[:cursor_pos])
    if match:
        class_name = match.group(1)
        if method == 'onstart':
            if class_name in classMethodsforOnStart:
                filtered_list = classMethodsforOnStart[class_name]
        elif method == 'onprocess':
            if class_name in classMethodsforOnProcess:
                filtered_list = classMethodsforOnProcess[class_name]
        elif method == 'onend':
            if class_name in classMethodsforOnEnd:
                filtered_list = classMethodsforOnEnd[class_name]
        else:
            filtered_list = []
    else:
        filtered_list = [kw for kw in commonJavaKeyWords if kw.startswith(line[cursor_pos:])]
    
    return filtered_list


def read_javap_result(app):
    try:
        result = {}
        file_path = app.config['path_of_interfaceOnly_javap']
        tempClassName = ''
        tempClass = []
        with open(file_path, 'r') as file:
            for line in file:
                content = line.strip()
                # detect the class
                if ' class ' in content and ' {' in content:
                    tempClassName = content.replace('public class ', '').replace(' {', '').strip()
                    tempClassName = tempClassName.split('.')[-1]
                    result[tempClassName] = {}
                    tempClass = result[tempClassName]
                    tempClass['variables'] = set()
                    tempClass['methods'] = set()
                if len(content) > 0 and 'public' in content and tempClassName not in content:
                    if '(' not in content:
                        tempClass['variables'].add(content.replace('public ', '').replace(';', ''))
                    else:  
                        tempMethod = content.replace('public ', '').replace(';', '')
                        tempMethod = tempMethod[:tempMethod.index(')') + 1]
                        tempMethod = tempMethod.split(' ')[-1]
                        tempClass['methods'].add(tempMethod)

        result.pop('ForFutureData')
        result.pop('Order')
        result.pop('Profile')
        result.pop('Main')
        result.pop('Action>')

        for k, v in result.items():
            print(f"Class: {k}")
            print(f"Variables: {v['variables']}")
            print(f"Methods: {v['methods']}")
            print() 
            if v['methods'] is not None:
                classMethodsforOnStart[k] = list(v['methods']) + list(v['variables'])
                if(k == 'FutureDataStructure'):
                    classMethodsforOnProcess['data'] = list(v['methods']) + list(v['variables'])
                else:
                    classMethodsforOnProcess[k] = list(v['methods']) + list(v['variables'])
                classMethodsforOnEnd[k] = list(v['methods']) + list(v['variables'])
            
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")