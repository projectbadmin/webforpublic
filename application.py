import argparse
import configparser
import os
import subprocess
from flask import  Flask, jsonify, render_template, request
import json
from applogging import init_logging
from processUserCode import process, realTimeUpdateLog, checkSyntax
from cloudbatchjobinjava import check_and_generate_keywords_, read_javap_result

application = Flask(__name__)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run the Flask app with a specific environment.')
parser.add_argument('--env', type=str, default='beanstalkinstance', help='Environment to run the app in (local, cloud)')
args = parser.parse_args()
env = args.env

# load the config file
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    application.config['env'] = env
    application.config['https_of_cloudBatchJobTemplateDevelopment'] = config.get(env, 'https_of_cloudBatchJobTemplateDevelopment')
    application.config['clone_of_cloudBatchJobTemplate'] = config.get(env, 'clone_of_cloudBatchJobTemplate')
    application.config['logDirectory_of_cloudBatchJobTemplate'] = config.get(env, 'logDirectory_of_cloudBatchJobTemplate')
    application.config['logDirectory_of_webforpublic'] = config.get(env, 'logDirectory_of_webforpublic')
    application.config['AWS_ACCESS_KEY_ID'] = config.get(env, 'AWS_ACCESS_KEY_ID')
    application.config['AWS_SECRET_ACCESS_KEY'] = config.get(env, 'AWS_SECRET_ACCESS_KEY')
    application.config['path_of_interfaceOnly_javap'] = config.get(env, 'path_of_interfaceOnly_javap')
except Exception as e:
    application.logger.error(e)

# create necessary directory
if not os.path.exists(application.config['clone_of_cloudBatchJobTemplate']):
    os.makedirs(application.config['clone_of_cloudBatchJobTemplate'])
    os.chmod(application.config['clone_of_cloudBatchJobTemplate'], 0o777)
if not os.path.exists(application.config['logDirectory_of_cloudBatchJobTemplate']):
    os.makedirs(application.config['logDirectory_of_cloudBatchJobTemplate'])
    os.chmod(application.config['logDirectory_of_cloudBatchJobTemplate'], 0o777)
if not os.path.exists(application.config['logDirectory_of_webforpublic']):
    os.makedirs(application.config['logDirectory_of_webforpublic'])
    os.chmod(application.config['logDirectory_of_webforpublic'], 0o777)

# download necessary the file
if application.config['env'] != 'local':
    # Set environment variables
    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = application.config['AWS_ACCESS_KEY_ID']
    env['AWS_SECRET_ACCESS_KEY'] = application.config['AWS_SECRET_ACCESS_KEY']
    subprocess.run([f"aws s3 cp s3://git-cloudbatchjobtemplatedevelopment/interfaceOnly_javap.txt {application.config['path_of_interfaceOnly_javap']}"], capture_output=True, text=True, shell=True)

# initialize logging
init_logging(application)
application.logger.info('Initialized logging')

# Configure your application and register blueprints here


@application.route('/')
def index():
    return "Your Flask application is running!"

@application.route('/cloudbatchjobingui')
def cloudbatchjobingui():
    read_javap_result(application)
    return render_template('cloudbatchjobingui.html')

@application.route('/cloudbatchjobinjava')
def cloudbatchjobinjava():
    read_javap_result(application)
    return render_template('cloudbatchjobinjava.html')

@application.route('/cloudbatchjobinjava/check_and_generate_keywords', methods=['POST'])
def check_and_generate_keywords():
    data = request.get_json()
    line = data.get('line')
    cursor_pos = data.get('cursor_pos')
    method = data.get('method')
    output = check_and_generate_keywords_(line, cursor_pos, method)
    return jsonify({'output': output})

@application.route('/cloudbatchjobinjava/submit', methods=['POST'])
def submitCloudbatchjobinjava():
    requestid = request.form['requestid']
    requestContentInJSON = json.loads(request.form['requestContentInJSON'])
    code_for_onStart = request.form['code_for_onStart']
    code_for_onProcess = request.form['code_for_onProcess']
    code_for_onEnd = request.form['code_for_onEnd']
    # process the code
    process(application, code_for_onStart, code_for_onProcess, code_for_onEnd, requestid, requestContentInJSON)
    # return the output
    return render_template('cloudbatchjobinjava.html', output='', requestid=requestid, requestContentInJSON=requestContentInJSON, code_for_onStart=code_for_onStart, code_for_onProcess=code_for_onProcess, code_for_onEnd=code_for_onEnd)


@application.route('/cloudbatchjobinjava/latest_output', methods=['POST'])
def get_latest_output():
    data = request.get_json()
    requestid = data['requestid']
    output = realTimeUpdateLog(application, request.get_json())
    return jsonify({'output': output})


@application.route('/cloudbatchjobinjava/check_syntax_for_onStart', methods=['POST'])
def check_syntax_for_onStart():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onStart = data['code_for_onStart']
    result = checkSyntax(application, "onStart", code_for_onStart, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@application.route('/cloudbatchjobinjava/check_syntax_for_onProcess', methods=['POST'])
def check_syntax_for_onProcess():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onProcess = data['code_for_onProcess']
    result = checkSyntax(application, "onProcess", code_for_onProcess, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@application.route('/cloudbatchjobinjava/check_syntax_for_onEnd', methods=['POST'])
def check_syntax_for_onEnd():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onEnd = data['code_for_onEnd']
    result = checkSyntax(application, "onEnd", code_for_onEnd, requestid, requestContentInJSON)
    return jsonify({'errors': result})


if __name__ == '__main__':
    application.run(port=5000, debug=True)
    #application.run(host='0.0.0.0', port=5001, debug=True)