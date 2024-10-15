from flask import Flask, jsonify, render_template, request
import configparser
import argparse
import json

from applogging import init_logging
from processUserCode import process, realTimeUpdateLog, checkSyntax

app = Flask(__name__)

# initialize logging
init_logging(app)
app.logger.info('Initialized logging')

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run the Flask app with a specific environment.')
parser.add_argument('--env', type=str, default='local', help='Environment to run the app in (local, cloud)')
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
    app.config['AWS_ACCESS_KEY_ID'] = config.get(env, 'AWS_ACCESS_KEY_ID')
    app.config['AWS_SECRET_ACCESS_KEY'] = config.get(env, 'AWS_SECRET_ACCESS_KEY')
except Exception as e:
    app.logger.error(e)

@app.route('/cloudbatchjobinjava')
def cloudbatchjobinjava():
    return render_template('cloudbatchjobinjava.html')

@app.route('/submitCloudbatchjobinjava', methods=['POST'])
def submitCloudbatchjobinjava():
    requestid = request.form['requestid']
    requestContentInJSON = json.loads(request.form['requestContentInJSON'])
    code_for_onStart = request.form['code_for_onStart']
    code_for_onPrcoess = request.form['code_for_onPrcoess']
    code_for_onEnd = request.form['code_for_onEnd']
    
    # process the code
    process(app, code_for_onStart, code_for_onPrcoess, code_for_onEnd, requestid, requestContentInJSON)
    
    # return the output
    return render_template('cloudbatchjobinjava.html', output='', requestid=requestid, requestContentInJSON=requestContentInJSON, code_for_onStart=code_for_onStart, code_for_onPrcoess=code_for_onPrcoess, code_for_onEnd=code_for_onEnd)


@app.route('/latest_output', methods=['GET'])
def get_latest_output():
    requestid = request.args.get('requestid')
    output = realTimeUpdateLog(app, requestid)
    return jsonify({'output': output})


@app.route('/check_syntax_for_onStart', methods=['POST'])
def check_syntax_for_onStart():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onStart = data['code_for_onStart']
    result = checkSyntax(app, "onStart", code_for_onStart, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@app.route('/check_syntax_for_onProcess', methods=['POST'])
def check_syntax_for_onProcess():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onProcess = data['code_for_onProcess']
    result = checkSyntax(app, "onProcess", code_for_onProcess, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@app.route('/check_syntax_for_onEnd', methods=['POST'])
def check_syntax_for_onEnd():
    data = request.get_json()
    requestid = data['requestid']
    requestContentInJSON = json.loads(data['requestContentInJSON'])
    code_for_onEnd = data['code_for_onEnd']
    result = checkSyntax(app, "onEnd", code_for_onEnd, requestid, requestContentInJSON)
    return jsonify({'errors': result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)