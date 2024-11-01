from flask import Flask, jsonify, render_template, request
import configparser
import argparse
import json

from applogging import init_logging
from processUserCode import process, realTimeUpdateLog, checkSyntax

from cloudbatchjobinjava import check_and_generate_keywords_, read_javap_result

app = Flask(__name__)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run the Flask app with a specific environment.')
parser.add_argument('--env', type=str, default='cloud', help='Environment to run the app in (local, cloud)')
args = parser.parse_args()
env = args.env

# load the config file
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    app.config['env'] = env
    app.config['https_of_cloudBatchJobTemplateDevelopment'] = config.get(env, 'https_of_cloudBatchJobTemplateDevelopment')
    app.config['clone_of_cloudBatchJobTemplate'] = config.get(env, 'clone_of_cloudBatchJobTemplate')
    app.config['logDirectory_of_cloudBatchJobTemplate'] = config.get(env, 'logDirectory_of_cloudBatchJobTemplate')
    app.config['logDirectory_of_webforpublic'] = config.get(env, 'logDirectory_of_webforpublic')
    app.config['AWS_ACCESS_KEY_ID'] = config.get(env, 'AWS_ACCESS_KEY_ID')
    app.config['AWS_SECRET_ACCESS_KEY'] = config.get(env, 'AWS_SECRET_ACCESS_KEY')
    app.config['path_of_interfaceOnly_javap'] = config.get(env, 'path_of_interfaceOnly_javap')
except Exception as e:
    app.logger.error(e)

# initialize logging
init_logging(app)
app.logger.info('Initialized logging')

@app.route('/cloudbatchjobingui')
def cloudbatchjobingui():
    read_javap_result(app)
    return render_template('cloudbatchjobingui.html')

@app.route('/cloudbatchjobinjava')
def cloudbatchjobinjava():
    read_javap_result(app)
    return render_template('cloudbatchjobinjava.html')

@app.route('/cloudbatchjobinjava/check_and_generate_keywords', methods=['POST'])
def check_and_generate_keywords():
    data = request.get_json()
    line = data.get('line')
    cursor_pos = data.get('cursor_pos')
    method = data.get('method')
    output = check_and_generate_keywords_(line, cursor_pos, method)
    return jsonify({'output': output})

@app.route('/cloudbatchjobinjava/submit', methods=['POST'])
def submitCloudbatchjobinjava():
    requestid = request.form['requestid']
    requestContentInJSON = json.loads(request.form['requestContentInJSON'])
    code_for_onStart = request.form['code_for_onStart']
    code_for_onProcess = request.form['code_for_onProcess']
    code_for_onEnd = request.form['code_for_onEnd']
    # process the code
    process(app, code_for_onStart, code_for_onProcess, code_for_onEnd, requestid, requestContentInJSON)
    # return the output
    return render_template('cloudbatchjobinjava.html', output='', requestid=requestid, requestContentInJSON=requestContentInJSON, code_for_onStart=code_for_onStart, code_for_onProcess=code_for_onProcess, code_for_onEnd=code_for_onEnd)


@app.route('/cloudbatchjobinjava/latest_output', methods=['POST'])
def get_latest_output():
    data = request.get_json()
    requestid = data['requestid']
    output = realTimeUpdateLog(app, request.get_json())
    return jsonify({'output': output})


@app.route('/cloudbatchjobinjava/check_syntax_for_onStart', methods=['POST'])
def check_syntax_for_onStart():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onStart = data['code_for_onStart']
    result = checkSyntax(app, "onStart", code_for_onStart, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@app.route('/cloudbatchjobinjava/check_syntax_for_onProcess', methods=['POST'])
def check_syntax_for_onProcess():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onProcess = data['code_for_onProcess']
    result = checkSyntax(app, "onProcess", code_for_onProcess, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@app.route('/cloudbatchjobinjava/check_syntax_for_onEnd', methods=['POST'])
def check_syntax_for_onEnd():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onEnd = data['code_for_onEnd']
    result = checkSyntax(app, "onEnd", code_for_onEnd, requestid, requestContentInJSON)
    return jsonify({'errors': result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
