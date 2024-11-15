from flask import  Flask, jsonify, redirect, render_template, request, session, url_for
import json
from applogging import init_logging
from commonFunction import check_logged_in_or_not, send_post_request
from home import get_dataStreamingList, request_newJob
from initialize import initialize
from processUserCode import process, realTimeUpdateLog, checkSyntax
from cloudbatchjobinjava import check_and_generate_keywords_, read_javap_result

application = Flask(__name__)
initialize(application)

@application.route('/home')
def home():
    data_streaming_list = get_dataStreamingList()
    content = "Your Flask application is running!"
    config_settings = {
        'env': application.config['env'],
        'https_of_cloudBatchJobTemplateDevelopment': application.config['https_of_cloudBatchJobTemplateDevelopment'],
        'clone_of_cloudBatchJobTemplate': application.config['clone_of_cloudBatchJobTemplate'],
        'logDirectory_of_cloudBatchJobTemplate': application.config['logDirectory_of_cloudBatchJobTemplate'],
        'logDirectory_of_webforpublic': application.config['logDirectory_of_webforpublic'],
        'AWS_ACCESS_KEY_ID': application.config['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': application.config['AWS_SECRET_ACCESS_KEY'],
        'path_of_interfaceOnly_javap': application.config['path_of_interfaceOnly_javap']
    }
    session_info = {
        'permanent': session.permanent,
        'new': session.new,
        'modified': session.modified,
        'userid': session.get('userid', 'No userid found'),
        'cookie': session.get('cookie', 'No cookie found')
    }
    content += f"<pre>{json.dumps(session_info, indent=4)}</pre>"
    content += f"<pre>{json.dumps(config_settings, indent=4)}</pre>"
    return render_template('home.html', data_streaming_list=data_streaming_list, content=content)

@application.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = send_post_request(
            'https://nk32qyplih.execute-api.ap-south-1.amazonaws.com/Login', 
            {'USERNAME': username, 'PASSWORD': password}
        )
        message = response.get('message', 'No message found')
        if message == "Login successful":
            session.permanent = True
            session['userid'] = response.get('userid', None)
            session['cookie'] = response.get('cookie', None)
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@application.route('/logout', methods=['GET'])
def logout():
    send_post_request('https://b22md47un2.execute-api.ap-south-1.amazonaws.com/Logout', {})
    session.clear()
    return "Redirecting to login page..."

@application.route('/cloudbatchjobingui')
def cloudbatchjobingui():
    read_javap_result(application)
    return render_template('cloudbatchjobingui.html')

@application.route('/cloudbatchjobinjava', methods=['GET', 'POST'])
def cloudbatchjobinjava():
    read_javap_result(application)
    if request.method == 'POST':
        # Retrieve requestid and requestContentInJSON from the form data
        requestid = request.form.get('requestid')
        requestContentInJSON = request.form.get('requestContentInJSON')

        # If requestContentInJSON is a JSON string, parse it
        if requestContentInJSON:
            requestContentInJSON = json.loads(requestContentInJSON)

        return render_template('cloudbatchjobinjava.html', requestid=requestid, requestContentInJSON=json.dumps(requestContentInJSON))
    else:
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
    output = realTimeUpdateLog(application, requestid)
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


@application.route('/request-new-data-streaming', methods=['POST'])
def request_new_data_streaming():
    datetimeselectiontype = request.form['datetime-selection-type']
    fromdate = request.form['from-date']
    todate = request.form['to-date']
    fromtime = request.form['from-time']
    totime = request.form['to-time']
    class_code = request.form['class-code']
    fut_opt = request.form['fut-opt']
    expiry_mth = request.form['expiry-mth']
    strike_prc = request.form['strike-prc']
    call_put = request.form['call-put']
    retention_hour = request.form['retention-hour']
    response = request_newJob(datetimeselectiontype, fromdate, todate, fromtime, totime, class_code, fut_opt, expiry_mth, strike_prc, call_put, retention_hour)
    message = response.get('message', 'No message found')
    if message == "request successful":
        requestid = response.get('DATA_STREAM_ID', 'No message found')
        requestContentInJSON = response.get('requestContentInJSON', 'No message found')
        return render_template('cloudbatchjobinjava.html', requestid=requestid, requestContentInJSON=json.dumps(requestContentInJSON))
    else:
        return "Invalid credentials"

# Register the function to run before each request
@application.before_request
def before_request():
    if request.method not in ['GET', 'POST']:
        return "Method not allowed", 405
    logged_in = check_logged_in_or_not()
    if not logged_in and request.endpoint != 'login':
        return redirect(url_for('login'))

if __name__ == '__main__':
    application.run(port=8000, debug=True)
    #application.run(host='0.0.0.0', port=5001, debug=True)