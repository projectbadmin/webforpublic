from flask import  Flask, Response, jsonify, redirect, render_template, request, session, stream_template, url_for
import json
from applogging import init_logging
from cloudbatchjobresult import fetch_result
from commonFunction import check_logged_in_or_not, send_post_request
from home import get_dataStreamingList, request_newJob
from initialize import initialize
from processUserCode import checkSyntaxBeforeCompile, process, realTimeUpdateLog, checkSyntax
from cloudbatchjobinjava import check_and_generate_keywords_, cloudbatchjobinjava, cloudbatchjobinjava_edit_program_file, read_javap_result

application = Flask(__name__)
initialize(application)


@application.route('/')
def index():
    return redirect(url_for('home'))

@application.route('/home')
def home():
    data_streaming_list = get_dataStreamingList("","","","","")
    return render_template('home.html', data_streaming_list=data_streaming_list)

@application.route('/login', methods=['GET','POST'])
def login():
    logged_in = check_logged_in_or_not()
    if logged_in:
        return redirect(url_for('home'))
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
    return redirect(url_for('login'))

@application.route('/cloudbatchjobingui')
def cloudbatchjobingui():
    read_javap_result(application)
    return render_template('cloudbatchjobingui.html')

@application.route('/cloudbatchjobinjava/check_and_generate_keywords', methods=['POST'])
def check_and_generate_keywords():
    data = request.get_json()
    line = data.get('line')
    cursor_pos = data.get('cursor_pos')
    method = data.get('method')
    output = check_and_generate_keywords_(line, cursor_pos, method)
    return jsonify({'output': output})

@application.route('/cloudbatchjobinjava/submit/<tempPageRequestID>', methods=['POST'])
def submitCloudbatchjobinjava(tempPageRequestID):
    tempPageRequestID_value = session.get(tempPageRequestID, 'No request found')
    if(tempPageRequestID_value=='No request found'):
        return render_template('error.html', error_message="No request found")
    requestid = tempPageRequestID_value['requestid']
    job_alias = request.form['job_alias']
    requestContentInJSON = tempPageRequestID_value['requestContentInJSON']
    code_for_onStart = request.form['code_for_onStart']
    code_for_onProcess = request.form['code_for_onProcess']
    code_for_onEnd = request.form['code_for_onEnd']
    result = checkSyntaxBeforeCompile(application, code_for_onStart, code_for_onProcess, code_for_onEnd, requestid, requestContentInJSON)
    if(result != ""):
        return render_template('error.html', error_message=result)
    # process the code
    process(application, code_for_onStart, code_for_onProcess, code_for_onEnd, requestid, requestContentInJSON, job_alias)
    # return the output
    return redirect(url_for('home'))


@application.route('/cloudbatchjobinjava/latest_output', methods=['POST'])
def get_latest_output():
    data = request.get_json()
    tempPageRequestID = data['tempPageRequestID']
    output = realTimeUpdateLog(application, tempPageRequestID)
    return jsonify({'output': output})


@application.route('/cloudbatchjobinjava/check_syntax_for_onStart', methods=['POST'])
def check_syntax_for_onStart():
    data = request.get_json()
    tempPageRequestID = data['tempPageRequestID']
    tempPageRequestID_value = session.get(tempPageRequestID, 'No request found')
    if(tempPageRequestID_value=='No request found'):
        return jsonify({'errors': tempPageRequestID_value})
    requestid = tempPageRequestID_value['requestid']
    requestContentInJSON = tempPageRequestID_value['requestContentInJSON']
    code_for_onStart = data['code_for_onStart']
    result = checkSyntax(application, "onStart", code_for_onStart, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@application.route('/cloudbatchjobinjava/check_syntax_for_onProcess', methods=['POST'])
def check_syntax_for_onProcess():
    data = request.get_json()
    tempPageRequestID = data['tempPageRequestID']
    tempPageRequestID_value = session.get(tempPageRequestID, 'No request found')
    if(tempPageRequestID_value=='No request found'):
        return jsonify({'errors': tempPageRequestID_value})
    requestid = tempPageRequestID_value['requestid']
    requestContentInJSON = tempPageRequestID_value['requestContentInJSON']
    code_for_onProcess = data['code_for_onProcess']
    result = checkSyntax(application, "onProcess", code_for_onProcess, requestid, requestContentInJSON)
    return jsonify({'errors': result})

@application.route('/cloudbatchjobinjava/check_syntax_for_onEnd', methods=['POST'])
def check_syntax_for_onEnd():
    data = request.get_json()
    tempPageRequestID = data['tempPageRequestID']
    tempPageRequestID_value = session.get(tempPageRequestID, 'No request found')
    if(tempPageRequestID_value=='No request found'):
        return jsonify({'errors': tempPageRequestID_value})
    requestid = tempPageRequestID_value['requestid']
    requestContentInJSON = tempPageRequestID_value['requestContentInJSON']
    code_for_onEnd = data['code_for_onEnd']
    result = checkSyntax(application, "onEnd", code_for_onEnd, requestid, requestContentInJSON)
    return jsonify({'errors': result})


@application.route('/home/request-new-data-streaming', methods=['POST'])
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
        cloudbatchjobinjava_template = cloudbatchjobinjava(application, requestid, requestContentInJSON)
        return cloudbatchjobinjava_template
    else:
        return redirect(url_for('home'))
    

@application.route('/home/use-data-streaming/<stream_id>')
def use_data_streaming(stream_id):
    filtered_list = get_dataStreamingList("", "", "", stream_id, "")
    if len(filtered_list) == 0:
        return "Invalid stream id"
    requestid = filtered_list[0].get('ID', 'No message found')
    requestContentInJSON = filtered_list[0].get('REQUEST_CONTENT', 'No message found')
    cloudbatchjobinjava_template = cloudbatchjobinjava(application, requestid, requestContentInJSON)
    return cloudbatchjobinjava_template
    

@application.route('/home/use-data-streaming/<stream_id>/<cloudbatchjob_id>')
def use_data_streaming_and_edit_program_file(stream_id, cloudbatchjob_id):
    filtered_list = get_dataStreamingList("", "", "", stream_id, cloudbatchjob_id)
    if len(filtered_list) == 0:
        return "Invalid stream id"
    requestid = filtered_list[0].get('ID', 'No message found')
    requestContentInJSON = filtered_list[0].get('REQUEST_CONTENT', 'No message found')
    cloudbatchjoblist = filtered_list[0].get('CLOUDBATCHJOBLIST')
    if len(cloudbatchjoblist) > 0:
        alias = cloudbatchjoblist[0].get('ALIAS', 'No message found')
    else:
        cloudbatchjob_in_session = session.get(cloudbatchjob_id, 'No cloudbatchjob_id found')
        alias = cloudbatchjob_in_session.get('ALIAS', 'No message found')
    application.logger.info('3333 --- CloudBatchJobLocalDraft:' + str(session.get('CloudBatchJobLocalDraft')))
    application.logger.info('4444 --- CloudBatchJobLocalDraft:' + str(session['CloudBatchJobLocalDraft']))
    cloudbatchjobinjava_template = cloudbatchjobinjava_edit_program_file(application, requestid, requestContentInJSON, cloudbatchjob_id, alias)
    return cloudbatchjobinjava_template


@application.route('/home/use-data-streaming/save/<tempPageRequestID>', methods=['POST'])
def use_data_streaming_and_save(tempPageRequestID):
    tempPageRequestID_value = session.get(tempPageRequestID, 'No request found')
    if(tempPageRequestID_value=='No request found'):
        return render_template('error.html', error_message="No request found")
    requestid = tempPageRequestID_value['requestid']
    job_alias = request.form['job_alias']
    requestContentInJSON = tempPageRequestID_value['requestContentInJSON']
    code_for_onStart = request.form['code_for_onStart']
    code_for_onProcess = request.form['code_for_onProcess']
    code_for_onEnd = request.form['code_for_onEnd']

    temp_session_value =  {
        'requestid': requestid,
        'job_alias': job_alias,
        'requestContentInJSON': requestContentInJSON,
        'code_for_onStart': code_for_onStart,
        'code_for_onProcess': code_for_onProcess,
        'code_for_onEnd': code_for_onEnd,
        'status': 'DRAFT',
        'ALIAS': job_alias,
        'STATUS': 'DRAFT',
        'ID': tempPageRequestID
    }

    if session.get('CloudBatchJobLocalDraft', None) is None:
        session['CloudBatchJobLocalDraft'] = []

    # check if the cloudbatchjob is in draft    
    new_temp_session_value = []
    for i in range(len(session['CloudBatchJobLocalDraft'])):
        if session['CloudBatchJobLocalDraft'][i]['ID'] != tempPageRequestID:
            new_temp_session_value.append(session['CloudBatchJobLocalDraft'][i])
    
    new_temp_session_value.append(temp_session_value)

    session['CloudBatchJobLocalDraft'] = new_temp_session_value
    session.modified = True

    return "Draft saved successfully"
    

@application.route('/home/view-cloudbatchjob-result/<stream_id>/<cloudbatchjob_id>')
def view_cloudbatchjob_result(stream_id, cloudbatchjob_id):
    return render_template('cloudbatchjobresult.html', stream_id=stream_id, cloudbatchjob_id=cloudbatchjob_id)


@application.route('/home/view-cloudbatchjob-result/fetch', methods=['POST'])
def fetch_cloudbatchjob_result():
    data = request.get_json()
    stream_id = data['stream_id']
    cloudbatchjob_id = data['cloudbatchjob_id']
    result = fetch_result(application, stream_id, cloudbatchjob_id)
    return result


# Register the function to run before each request
@application.before_request
def before_request():
    if request.endpoint != 'login':
        if request.method not in ['GET', 'POST']:
            return "Method not allowed", 405
        logged_in = check_logged_in_or_not()
        if not logged_in:
            session.clear()
            return redirect(url_for('login'))

if __name__ == '__main__':
    application.run(port=8000, debug=True)
    #application.run(host='0.0.0.0', port=5001, debug=True)