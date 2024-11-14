from flask import  Flask, jsonify, redirect, render_template, request, session, url_for
import json
from applogging import init_logging
from commonFunction import send_post_request
from initialize import initialize
from processUserCode import process, realTimeUpdateLog, checkSyntax
from cloudbatchjobinjava import check_and_generate_keywords_, read_javap_result

app = Flask(__name__)
initialize(app)

@app.route('/home')
def home():
    content = "Your Flask app is running!"
    config_settings = {
        'env': app.config['env'],
        'https_of_cloudBatchJobTemplateDevelopment': app.config['https_of_cloudBatchJobTemplateDevelopment'],
        'clone_of_cloudBatchJobTemplate': app.config['clone_of_cloudBatchJobTemplate'],
        'logDirectory_of_cloudBatchJobTemplate': app.config['logDirectory_of_cloudBatchJobTemplate'],
        'logDirectory_of_webforpublic': app.config['logDirectory_of_webforpublic'],
        'AWS_ACCESS_KEY_ID': app.config['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': app.config['AWS_SECRET_ACCESS_KEY'],
        'path_of_interfaceOnly_javap': app.config['path_of_interfaceOnly_javap']
    }
    session_info = {
        'permanent': session.permanent,
        'new': session.new,
        'modified': session.modified,
        'cookie': session.get('cookie', 'No cookie found')
    }
    content += f"<pre>{json.dumps(session_info, indent=4)}</pre>"
    content += f"<pre>{json.dumps(config_settings, indent=4)}</pre>"
    return content

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = send_post_request('https://nk32qyplih.execute-api.ap-south-1.amazonaws.com/Login', {'USERNAME': username, 'PASSWORD': password})
        message = response.get('message', 'No message found')
        if message == "Login successful":
            session.permanent = True
            session['cookie'] = response.get('cookie', 'No cookie found')
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

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
    output = realTimeUpdateLog(app, requestid)
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
    app.run(port=8000, debug=True)
    #app.run(host='0.0.0.0', port=5001, debug=True)